// Minimal CDCL SAT solver written for this audit (not Kissat/CaDiCaL).
// 2-watched literals, 1UIP learning with local minimization, VSIDS heap,
// phase saving, Luby restarts, LBD-based learnt-clause reduction.
// Usage: cdcl file.cnf [max_conflicts] [max_seconds] [model_out]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef struct { int *a; int n, cap; } vec;
static void push(vec *v, int x) {
  if (v->n == v->cap) { v->cap = v->cap ? v->cap * 2 : 4; v->a = realloc(v->a, sizeof(int) * v->cap); }
  v->a[v->n++] = x;
}
#define VAR(l) ((l) >> 1)
#define NEG(l) ((l) ^ 1)
#define SIGN(l) ((l) & 1)

static int nvars;
static int *arena; static long asz, acap;
static vec *watches;
static signed char *val, *phase;
static int *level, *reason, *trail, tn, qhead, *trail_lim, nlim;
static double *act, var_inc = 1.0;
static int *heap, hn, *hpos;
static char *seen;
static vec learnts;
static long conflicts, decisions, propagations;

static inline int lv(int l) { int v = val[VAR(l)]; return SIGN(l) ? -v : v; }

static void heap_up(int i) {
  int x = heap[i];
  while (i > 0) { int p = (i - 1) >> 1; if (act[heap[p]] >= act[x]) break; heap[i] = heap[p]; hpos[heap[i]] = i; i = p; }
  heap[i] = x; hpos[x] = i;
}
static void heap_down(int i) {
  int x = heap[i];
  for (;;) {
    int c = 2 * i + 1; if (c >= hn) break;
    if (c + 1 < hn && act[heap[c + 1]] > act[heap[c]]) c++;
    if (act[heap[c]] <= act[x]) break;
    heap[i] = heap[c]; hpos[heap[i]] = i; i = c;
  }
  heap[i] = x; hpos[x] = i;
}
static void heap_insert(int v) { if (hpos[v] >= 0) return; hpos[v] = hn; heap[hn++] = v; heap_up(hpos[v]); }
static int heap_pop(void) {
  int x = heap[0]; hpos[x] = -1; hn--;
  if (hn > 0) { heap[0] = heap[hn]; hpos[heap[0]] = 0; heap_down(0); }
  return x;
}
static void bump(int v) {
  act[v] += var_inc;
  if (act[v] > 1e100) { for (int i = 1; i <= nvars; i++) act[i] *= 1e-100; var_inc *= 1e-100; }
  if (hpos[v] >= 0) heap_up(hpos[v]);
}
static int new_clause(int *lits, int n, int learnt, int lbd) {
  if (asz + n + 2 > acap) { acap = (acap + n + 2) * 2; arena = realloc(arena, sizeof(int) * acap); }
  int c = (int)asz; arena[asz++] = n; arena[asz++] = (lbd << 1) | learnt;
  memcpy(arena + asz, lits, sizeof(int) * n); asz += n;
  if (n >= 2) { push(&watches[NEG(lits[0])], c); push(&watches[NEG(lits[1])], c); }
  return c;
}
static void enqueue(int l, int r) {
  int v = VAR(l); val[v] = SIGN(l) ? -1 : 1; level[v] = nlim; reason[v] = r; trail[tn++] = l;
}
static int propagate(void) {
  while (qhead < tn) {
    int p = trail[qhead++]; propagations++;
    vec *ws = &watches[p]; int i = 0, j = 0, fl = NEG(p);
    while (i < ws->n) {
      int c = ws->a[i++];
      int size = arena[c]; if (size == 0) continue;
      int *lits = arena + c + 2;
      if (lits[0] == fl) { lits[0] = lits[1]; lits[1] = fl; }
      if (lv(lits[0]) == 1) { ws->a[j++] = c; continue; }
      int found = 0;
      for (int k = 2; k < size; k++) if (lv(lits[k]) != -1) {
        lits[1] = lits[k]; lits[k] = fl; push(&watches[NEG(lits[1])], c); found = 1; break;
      }
      if (found) continue;
      ws->a[j++] = c;
      if (lv(lits[0]) == -1) { while (i < ws->n) ws->a[j++] = ws->a[i++]; ws->n = j; qhead = tn; return c; }
      enqueue(lits[0], c);
    }
    ws->n = j;
  }
  return -1;
}
static void backtrack(int lev) {
  if (nlim <= lev) return;
  for (int i = tn - 1; i >= trail_lim[lev]; i--) {
    int v = VAR(trail[i]); phase[v] = val[v]; val[v] = 0; reason[v] = -1; heap_insert(v);
  }
  tn = trail_lim[lev]; qhead = tn; nlim = lev;
}
static vec out;
static int analyze(int confl, int *btlevel, int *lbd_out) {
  out.n = 0; push(&out, 0);
  int pathC = 0, p = -1, idx = tn - 1;
  do {
    int *lits = arena + confl + 2, size = arena[confl];
    for (int k = 0; k < size; k++) {
      int q = lits[k]; if (q == p) continue;
      int v = VAR(q);
      if (!seen[v] && level[v] > 0) {
        bump(v); seen[v] = 1;
        if (level[v] >= nlim) pathC++; else push(&out, q);
      }
    }
    while (!seen[VAR(trail[idx])]) idx--;
    p = trail[idx]; idx--; confl = reason[VAR(p)]; seen[VAR(p)] = 0; pathC--;
  } while (pathC > 0);
  out.a[0] = NEG(p);
  // local minimization
  int j = 1;
  static vec toclear; toclear.n = 0;
  for (int i = 1; i < out.n; i++) push(&toclear, VAR(out.a[i]));
  for (int i = 1; i < out.n; i++) {
    int v = VAR(out.a[i]), r = reason[v], red = (r >= 0);
    if (red) {
      int *lits = arena + r + 2, size = arena[r];
      for (int k = 0; k < size; k++) { int u = VAR(lits[k]); if (u != v && !seen[u] && level[u] > 0) { red = 0; break; } }
    }
    if (!red) out.a[j++] = out.a[i];
  }
  out.n = j;
  for (int i = 0; i < toclear.n; i++) seen[toclear.a[i]] = 0;
  // backjump level and LBD
  int bt = 0, mi = 1;
  for (int i = 1; i < out.n; i++) if (level[VAR(out.a[i])] > bt) { bt = level[VAR(out.a[i])]; mi = i; }
  if (out.n > 1) { int t = out.a[1]; out.a[1] = out.a[mi]; out.a[mi] = t; }
  *btlevel = bt;
  static int *stamp; static int stampv; if (!stamp) stamp = calloc(nvars + 2, sizeof(int));
  stampv++; int lbd = 0;
  for (int i = 0; i < out.n; i++) { int l = level[VAR(out.a[i])]; if (stamp[l] != stampv) { stamp[l] = stampv; lbd++; } }
  *lbd_out = lbd;
  return out.n;
}
static int cmp_lbd(const void *a, const void *b) {
  int ca = *(const int *)a, cb = *(const int *)b;
  int la = arena[ca + 1] >> 1, lb = arena[cb + 1] >> 1;
  if (la != lb) return lb - la;
  return arena[cb] - arena[ca];
}
static void reduce_db(void) {
  vec cand = {0, 0, 0}; int j = 0;
  for (int i = 0; i < learnts.n; i++) {
    int c = learnts.a[i]; if (arena[c] == 0) continue;
    learnts.a[j++] = c;
    int *lits = arena + c + 2; int v = VAR(lits[0]);
    int locked = (val[v] != 0 && reason[v] == c);
    if (arena[c] > 2 && (arena[c + 1] >> 1) > 2 && !locked) push(&cand, c);
  }
  learnts.n = j;
  qsort(cand.a, cand.n, sizeof(int), cmp_lbd);
  for (int i = 0; i < cand.n / 2; i++) arena[cand.a[i]] = 0;
  free(cand.a);
}
static long luby(long x) {
  long size, seq;
  for (size = 1, seq = 0; size < x + 1; seq++, size = 2 * size + 1) ;
  while (size - 1 != x) { size = (size - 1) >> 1; seq--; x = x % size; }
  return 1L << seq;
}
int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage\n"); return 2; }
  long max_confl = argc > 2 ? atol(argv[2]) : 2000000; double max_sec = argc > 3 ? atof(argv[3]) : 300;
  FILE *f = fopen(argv[1], "r"); if (!f) { perror("open"); return 2; }
  int nclauses = 0; char line[1 << 16];
  while (fgets(line, sizeof line, f)) { if (line[0] == 'c') continue; if (line[0] == 'p') { sscanf(line, "p cnf %d %d", &nvars, &nclauses); break; } }
  watches = calloc(2 * nvars + 2, sizeof(vec)); val = calloc(nvars + 1, 1); phase = malloc(nvars + 1); memset(phase, -1, nvars + 1);
  level = calloc(nvars + 1, sizeof(int)); reason = malloc(sizeof(int) * (nvars + 1)); trail = malloc(sizeof(int) * (nvars + 1));
  trail_lim = malloc(sizeof(int) * (nvars + 2)); act = calloc(nvars + 1, sizeof(double)); heap = malloc(sizeof(int) * (nvars + 1));
  hpos = malloc(sizeof(int) * (nvars + 1)); seen = calloc(nvars + 1, 1);
  for (int i = 1; i <= nvars; i++) { reason[i] = -1; hpos[i] = -1; }
  for (int i = 1; i <= nvars; i++) heap_insert(i);
  vec cl = {0, 0, 0}; int x, unsat = 0; long nlits = 0, ncl = 0;
  vec units = {0, 0, 0};
  while (fscanf(f, "%d", &x) == 1) {
    if (x != 0) { push(&cl, x > 0 ? 2 * x : 2 * (-x) + 1); continue; }
    // dedupe / tautology
    int n = 0, taut = 0;
    for (int i = 0; i < cl.n && !taut; i++) {
      int dup = 0;
      for (int k = 0; k < n; k++) { if (cl.a[k] == cl.a[i]) dup = 1; if (cl.a[k] == NEG(cl.a[i])) taut = 1; }
      if (!dup) cl.a[n++] = cl.a[i];
    }
    if (!taut) { ncl++; nlits += n; if (n == 0) unsat = 1; else if (n == 1) push(&units, cl.a[0]); else new_clause(cl.a, n, 0, 0); }
    cl.n = 0;
  }
  fclose(f);
  clock_t t0 = clock();
  const char *res = "UNKNOWN";
  for (int i = 0; i < units.n && !unsat; i++) { int l = units.a[i]; if (lv(l) == -1) unsat = 1; else if (lv(l) == 0) enqueue(l, -1); }
  if (!unsat && propagate() >= 0) unsat = 1;
  long restart_i = 0, next_restart = 100 * luby(0), confl_at_restart = 0, next_reduce = 4000;
  if (unsat) res = "UNSATISFIABLE";
  else for (;;) {
    int confl = propagate();
    if (confl >= 0) {
      conflicts++;
      if (nlim == 0) { res = "UNSATISFIABLE"; break; }
      int bt, lbd, n = analyze(confl, &bt, &lbd);
      backtrack(bt);
      if (n == 1) enqueue(out.a[0], -1);
      else { int c = new_clause(out.a, n, 1, lbd); push(&learnts, c); enqueue(out.a[0], c); }
      var_inc *= 1.0 / 0.95;
      if (conflicts >= max_confl) break;
      if ((conflicts & 1023) == 0 && (double)(clock() - t0) / CLOCKS_PER_SEC > max_sec) break;
    } else {
      if (conflicts - confl_at_restart >= next_restart) { backtrack(0); confl_at_restart = conflicts; restart_i++; next_restart = 100 * luby(restart_i); }
      if (conflicts >= next_reduce && nlim == 0) { reduce_db(); next_reduce = conflicts + 4000 + 300 * (conflicts / 4000); }
      else if (conflicts >= next_reduce) { backtrack(0); reduce_db(); next_reduce = conflicts + 4000 + 300 * (conflicts / 4000); }
      int v = 0;
      while (hn > 0) { int u = heap_pop(); if (val[u] == 0) { v = u; break; } }
      if (!v) { res = "SATISFIABLE"; break; }
      decisions++; trail_lim[nlim++] = tn;
      enqueue(phase[v] == 1 ? 2 * v : 2 * v + 1, -1);
    }
  }
  double sec = (double)(clock() - t0) / CLOCKS_PER_SEC;
  printf("%s vars=%d clauses=%ld conflicts=%ld decisions=%ld props=%ld time=%.2fs\n", res, nvars, ncl, conflicts, decisions, propagations, sec);
  if (!strcmp(res, "SATISFIABLE") && argc > 4) {
    FILE *g = fopen(argv[4], "w");
    for (int i = 1; i <= nvars; i++) fprintf(g, "%d\n", val[i] == 1 ? i : -i);
    fclose(g);
  }
  return !strcmp(res, "SATISFIABLE") ? 10 : !strcmp(res, "UNSATISFIABLE") ? 20 : 0;
}

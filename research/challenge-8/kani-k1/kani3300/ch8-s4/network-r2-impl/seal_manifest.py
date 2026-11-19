"""Seal the offline packet file inventory; does not run any validations/tools."""
from pathlib import Path
import hashlib,json
OUT=Path(__file__).resolve().parent
assert not any(p.is_symlink() or p.name=='__pycache__' for p in OUT.rglob('*'))
files={str(p.relative_to(OUT)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='MANIFEST.json'}
(OUT/'MANIFEST.json').write_text(json.dumps({'schema':'network-r2-impl-manifest-v1','self_excluded':'MANIFEST.json; containing Git commit binds these exact bytes','files':files},indent=2)+'\n')
print(json.dumps({'files':len(files),'status':'SEALED'}))

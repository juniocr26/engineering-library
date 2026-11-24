"""Small dated checkpoint; human-facing progress stays at the repository root."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def sha(path):
    digest=hashlib.sha256()
    with path.open("rb")as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            digest.update(block)
    return digest.hexdigest()


def run(args):
    baseline=json.loads((HERE/"baseline.json").read_text())
    now=datetime.datetime.now(datetime.timezone.utc)
    elapsed=(now-datetime.datetime.fromisoformat(baseline["start_utc"])).total_seconds()
    env=dict(os.environ,GIT_OPTIONAL_LOCKS="0")
    def git(*values):
        return subprocess.check_output(["git",*values],cwd=ROOT,env=env,text=True).strip()
    cachepath=HERE/"checkpoint-hash-cache.json"
    cache=json.loads(cachepath.read_text())if cachepath.exists()else{}
    paths=set()
    for directory in (HERE,ROOT/".local-backups/continuation-20261120"):
        if directory.exists():
            paths.update(path for path in directory.rglob("*")if path.is_file()and
                         "__pycache__"not in path.parts and "checkpoints"not in path.parts and path!=cachepath)
    paths.update(ROOT/name for name in ("AI_TRAINING_CAMPAIGN_REPORT.md","AI_TRAINING_FILE_INVENTORY.md",
                                       "AI_FINE_TUNING_READINESS.md","AI_TRAINING_RESUME.md",
                                       "agent/tools/documentation_lifecycle.py","agent/tools/documentation_maintenance.py",
                                       "backend/lib/documentation/command.rb","backend/lib/documentation/python_structure.py",
                                       "agent/tools/documentation_retrieval.py","agent/recovery/manifest.json"))
    records=[]
    critical={"backend/lib/documentation/command.rb","backend/lib/documentation/python_structure.py",
              "agent/tools/documentation_retrieval.py","agent/recovery/manifest.json"}
    for path in sorted(paths):
        relative=str(path.relative_to(ROOT));stat=path.stat()
        signature=[stat.st_ino,stat.st_size,stat.st_mtime_ns]
        previous=cache.get(relative)
        checksum=previous["sha256"]if relative not in critical and previous and previous["stat"]==signature else sha(path)
        after=path.stat()
        if [after.st_ino,after.st_size,after.st_mtime_ns]!=signature:
            raise ValueError("Checkpoint input changed while hashing: "+relative)
        cache[relative]={"stat":signature,"sha256":checksum}
        records.append({"path":relative,"sha256":checksum,"bytes":stat.st_size})
    cachepath.write_text(json.dumps(cache,indent=2)+"\n")
    name="checkpoint-"+now.strftime("%Y%m%dT%H%M%S")+".json"
    out=HERE/"checkpoints";out.mkdir(exist_ok=True)
    operational=json.loads((ROOT/"agent/recovery/manifest.json").read_text())
    pinned={row["path"]:row["sha256"]for row in operational["operational_files"]}
    current_source_pins={name:{"current_sha256":sha(ROOT/name),"manifest_sha256":pinned.get(name),
                               "matches":sha(ROOT/name)==pinned.get(name)}for name in sorted(critical-{"agent/recovery/manifest.json"})}
    record={"checkpoint_schema_version":2,"current_source_pin_checks":current_source_pins,
            "all_current_source_pins_match":all(row["matches"]for row in current_source_pins.values()),"at":now.isoformat(),"local":now.astimezone(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(),
            "elapsed_seconds":elapsed,"minimum_target_utc":baseline["minimum_target_utc"],
            "duration_minimum_reached":elapsed>=11*3600,"campaign_status":"ACTIVE",
            "workstream":args.workstream,"completed":args.completed,"pending":args.pending,
            "next_safe_action":args.next_action,"active_or_uncertain_operations":args.active_operation,
            "tests_executed":args.test_result,"artifacts":records,"head":git("rev-parse","HEAD"),
            "git_status":git("status","--short"),"index_sha256":sha(ROOT/".git/index"),
            "index_matches_baseline":sha(ROOT/".git/index")==baseline["index_sha256"],
            "disk_free_bytes":shutil.disk_usage(ROOT).free,
            "resource_limitations":"No observable quota exhaustion or hard deadline warning recorded; host availability cannot be guaranteed.",
            "training_steps":0,"new_neural_training":False}
    with(out/name).open("x")as stream:
        stream.write(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
    with(ROOT/"AI_TRAINING_CAMPAIGN_REPORT.md").open("a")as stream:
        stream.write("\n### Checkpoint "+record["local"]+"\n\nElapsed "+format(elapsed/3600,".3f")+" hours; campaign ACTIVE. Workstream: "+args.workstream+".\n\n"+
                     "Completed: "+"; ".join(args.completed)+".\n\nNext: "+args.next_action+".\n\nTechnical checkpoint: `"+str((out/name).relative_to(ROOT))+"`.\n")
    with(ROOT/"AI_TRAINING_RESUME.md").open("a")as stream:
        stream.write("\nLatest checkpoint at "+record["local"]+": `"+str((out/name).relative_to(ROOT))+"`. Next safe action: "+args.next_action+". Campaign remains ACTIVE; target not inferred from task completion.\n")
    print(json.dumps({"checkpoint":name,"elapsed_hours":elapsed/3600,"index_matches_baseline":record["index_matches_baseline"],"files":len(records)}))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--workstream",required=True)
    parser.add_argument("--completed",action="append",default=[])
    parser.add_argument("--pending",action="append",default=[])
    parser.add_argument("--next-action",required=True)
    parser.add_argument("--active-operation",action="append",default=[])
    parser.add_argument("--test-result",action="append",default=[])
    run(parser.parse_args())

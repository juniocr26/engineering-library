"""Run owned controls in the existing frontend runtime; no new test suite."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent


def run(version):
    if version not in (1,2):
        raise ValueError("fixed producer version required")
    oracle=json.loads((HERE/"javascript-module-control-oracle-v1.json").read_text())
    filename="javascript_module_observer_v"+str(version)+".cjs"
    producer="/sources/engineering-library/agent/research/continuation-20261120/"+filename
    program='''const fs=require("node:fs");
const observer=require(process.argv[1]);
const marker="/tmp/el-js-observer-owned-no-execution-marker-20261120";
if(fs.existsSync(marker))throw new Error("pre-existing marker;preserve and do not claim non-execution");
const cases=JSON.parse(fs.readFileSync(0,"utf8"));
const rows=[];
for(const c of cases){
 let r;
 try{r=observer.observe(observer.strictJson(Buffer.from(c.raw_request,"utf8")))}
 catch(error){r={status:"INCONCLUSIVE",reason:String(error.message)}}
 const alias=!c.require_alias_wire_citation||!!r.export_evidence;
 const noExecution=!fs.existsSync(marker);
 rows.push({id:c.id,expected:c.expected_status,observed:r.status,
   matches:r.status===c.expected_status&&alias&&noExecution,
   alias_wire_citation_checked:!!c.require_alias_wire_citation,
   alias_wire_present:alias,source_execution_marker_absent:noExecution,result:r});
}
process.stdout.write(JSON.stringify({node_version:process.version,rows}));
'''
    command=["docker","exec","-i","-e","NODE_PATH=/app/frontend/node_modules","-w","/app/frontend",
             "engineering-library-frontend-1","node","-e",program,producer]
    result=subprocess.run(command,input=json.dumps(oracle["cases"]).encode(),capture_output=True,timeout=120)
    (HERE/("javascript-module-controls-v"+str(version)+".stdout")).write_bytes(result.stdout)
    (HERE/("javascript-module-controls-v"+str(version)+".stderr")).write_bytes(result.stderr)
    if result.returncode:
        raise ValueError("existing runtime control execution failed;raw outputs preserved")
    body=json.loads(result.stdout)
    report={"at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"producer_file":filename,
            "producer_sha256":hashlib.sha256((HERE/filename).read_bytes()).hexdigest(),
            "command":command,"node_version":body["node_version"],"cases":body["rows"],
            "correct":sum(row["matches"]for row in body["rows"]),"n":len(body["rows"]),
            "classification":"OWNED_RESEARCH_CONTROLS_NOT_PUBLIC_HOLDOUT_OR_PERMANENT_SUITE",
            "new_infrastructure":False,"installed_packages":False,"model_calls":0}
    with(HERE/("javascript-module-controls-v"+str(version)+".json")).open("x")as stream:
        stream.write(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print([(r["id"],r["observed"],r["matches"])for r in body["rows"]])


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("version",type=int,choices=(1,2))
    run(parser.parse_args().version)

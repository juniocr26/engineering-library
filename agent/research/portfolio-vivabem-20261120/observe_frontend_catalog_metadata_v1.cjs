const fs=require("node:fs/promises"),path=require("node:path"),crypto=require("node:crypto");
(async()=>{
const slugs=["engineering-library","go-image-optimizer","payment-reconciliation-lab","rust-event-relay","url-shortener"];
const configured=process.env.DOCUMENTATION_ROOT??path.resolve(process.cwd(),"../docs");
let base;try{base=await fs.realpath(configured)}catch{console.log(JSON.stringify({status:"ROOT_UNAVAILABLE",configured_root_sha256:crypto.createHash("sha256").update(configured).digest("hex")}));return}
const rows=[];
for(let i=0;i<slugs.length;i++){
 const slug=slugs[i],candidate=path.join(base,slug,"en/links/catalog.json");
 const row={project_index:i,project_name_sha256:crypto.createHash("sha256").update(slug).digest("hex")};
 try{
 const info=await fs.lstat(candidate),physical=await fs.realpath(candidate);
 if(!info.isFile()||info.isSymbolicLink()||physical!==candidate||!physical.startsWith(base+path.sep)||info.size>2097152){row.status="UNSAFE_OR_OVERSIZE_METADATA_NOT_READ";rows.push(row);continue}
 const raw=await fs.readFile(candidate);const catalog=JSON.parse(raw.toString("utf8"));
 row.status="METADATA_READ";row.metadata_bytes=raw.length;row.metadata_sha256=crypto.createHash("sha256").update(raw).digest("hex");row.project_identity_matches=catalog.project===slug;
 const files=(catalog.files&&typeof catalog.files==="object"&&!Array.isArray(catalog.files))?Object.values(catalog.files):[];row.records=files.length;row.status_counts={};
 for(const rec of files){const s=["available","excluded","missing","unapproved"].includes(rec?.status)?rec.status:"other_or_invalid";row.status_counts[s]=(row.status_counts[s]??0)+1}
 row.available_records_with_snapshot_and_sha256=files.filter(r=>r?.status==="available"&&typeof r.snapshot==="string"&&typeof r.sha256==="string"&&/^[a-f0-9]{64}$/.test(r.sha256)).length;
 }catch(e){row.status=e.code==="ENOENT"?"METADATA_MISSING":e instanceof SyntaxError?"METADATA_PARSE_FAILED":"METADATA_READ_REFUSED_OR_FAILED";row.error_code=["ENOENT","EACCES","ENOTDIR"].includes(e.code)?e.code:null}
 rows.push(row)
}
console.log(JSON.stringify({status:"METADATA_ONLY_OBSERVATION",configured_root_sha256:crypto.createHash("sha256").update(configured).digest("hex"),root_matches_configured_path:base===path.resolve(configured),rows,chapter_or_snapshot_content_read:false,test_or_application_invoked:false}))
})().catch(()=>{console.error("ownedmetadataworkerfailed");process.exit(1)});

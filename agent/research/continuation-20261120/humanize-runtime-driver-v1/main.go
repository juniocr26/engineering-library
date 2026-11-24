// Owned finite synthetic observations; exact public package imported without edits.
package main
import("encoding/json";"fmt";"math/big";"os";"strconv";"strings"; h "github.com/dustin/go-humanize")
type Case struct{ID string `json:"id"`; Operation string `json:"operation"`; Input string `json:"input"`}
type Request struct{Cases []Case `json:"cases"`}
func ec(err error)string{if err==nil{return "none"};s:=err.Error();if strings.HasPrefix(s,"unhandled size name:"){return "unit"};if strings.HasPrefix(s,"too large:"){return "too-large"};return "number"}
func main(){if len(os.Args)!=2{panic("one owned protocol file required")};raw,e:=os.ReadFile(os.Args[1]);if e!=nil{panic(e)};var req Request;if e=json.Unmarshal(raw,&req);e!=nil{panic(e)};rows:=[]map[string]any{}
for _,c:=range req.Cases{r:=map[string]any{"id":c.ID,"operation":c.Operation,"input":c.Input};o:=map[string]string{}
switch c.Operation{
case "ParseBytes":v,e:=h.ParseBytes(c.Input);o["value"]=strconv.FormatUint(v,10);o["error_class"]=ec(e);if e!=nil{r["error"]=e.Error()}
case "ParseBigBytes":v,e:=h.ParseBigBytes(c.Input);o["value"]="";if v!=nil{o["value"]=v.String()};o["error_class"]=ec(e);if e!=nil{r["error"]=e.Error()}
case "Bytes","IBytes":v,e:=strconv.ParseUint(c.Input,10,64);if e!=nil{panic(e)};if c.Operation=="Bytes"{o["text"]=h.Bytes(v)}else{o["text"]=h.IBytes(v)}
case "BigBytes","BigIBytes","BigComma":v,ok:=new(big.Int).SetString(c.Input,10);if !ok{panic("bad owned integer")};switch c.Operation{case "BigBytes":o["text"]=h.BigBytes(v);case "BigIBytes":o["text"]=h.BigIBytes(v);case "BigComma":o["text"]=h.BigComma(v)};o["input_after"]=v.String()
case "ComputeSI":v,e:=strconv.ParseFloat(c.Input,64);if e!=nil{panic(e)};value,prefix:=h.ComputeSI(v);o["value"]=strconv.FormatFloat(value,'g',-1,64);o["prefix"]=prefix
case "ParseSI":value,unit,e:=h.ParseSI(c.Input);o["value"]=strconv.FormatFloat(value,'g',-1,64);o["unit"]=unit;o["error_class"]=ec(e)
default:panic("operation outside finite protocol")};r["observed"]=o;rows=append(rows,r)}
if e:=json.NewEncoder(os.Stdout).Encode(rows);e!=nil{fmt.Fprintln(os.Stderr,e);os.Exit(1)}}

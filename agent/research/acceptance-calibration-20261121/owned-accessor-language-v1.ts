// Owned language-semantics probe; no external project imports or execution.
type Mode = "normal" | "constructor-throws" | "finalizer-throws";
function ownedBox(mode: Mode = "normal", guard: "truthiness" | "undefined-only" = "truthiness") {
  let cached: any;
  let items: any = [1];
  let context: any = { owned: true };
  let constructorCalls = 0;
  function ownedFinalize(value: any) {
    if (mode === "finalizer-throws") throw new Error("owned finalizer fault");
    return value;
  }
  class OwnedConstruct {
    constructor(public rows: any[], public suppliedContext: any) {
      constructorCalls++;
      if (mode === "constructor-throws") throw new Error("owned constructor fault");
    }
  }
  const box = {
    success: false,
    get error(): any {
      const shouldBuild = guard === "truthiness" ? !cached : cached === undefined;
      if (shouldBuild) {
        cached = new OwnedConstruct(items.map(ownedFinalize), context);
        items = undefined as any;
        context = undefined as any;
      }
      return cached;
    },
    set error(value: Error) {
      cached = value;
      items = undefined as any;
      context = undefined as any;
    },
  };
  return {
    box,
    inspect() { return { constructor_calls: constructorCalls, items_cleared: items === undefined, context_cleared: context === undefined }; },
  };
}
const results: any[] = [];
{
  const h = ownedBox(); const first = h.box.error; const second = h.box.error;
  results.push({ id: "initial-two-reads", ...h.inspect(), same_identity: first === second });
}
{
  const h = ownedBox(); const replacement = new Error("owned replacement"); h.box.error = replacement;
  results.push({ id: "truthy-setter-before-read", returned_replacement: h.box.error === replacement, ...h.inspect() });
}
{
  const h = ownedBox(); (h.box as any).error = 0; let thrownName: string | null = null;
  try { void h.box.error; } catch (e: any) { thrownName = e.name; }
  results.push({ id: "falsy-setter-before-read", thrown_name: thrownName, ...h.inspect() });
}
for (const mode of ["constructor-throws", "finalizer-throws"] as Mode[]) {
  const h = ownedBox(mode); let thrownName: string | null = null;
  try { void h.box.error; } catch (e: any) { thrownName = e.name; }
  results.push({ id: mode, thrown_name: thrownName, ...h.inspect() });
}
{
  const h = ownedBox("normal", "undefined-only"); (h.box as any).error = 0;
  const returnedZero = h.box.error === 0;
  results.push({ id: "falsy-setter-undefined-only-control", returned_zero: returnedZero, ...h.inspect() });
}
(globalThis as any).ownedResults = results;

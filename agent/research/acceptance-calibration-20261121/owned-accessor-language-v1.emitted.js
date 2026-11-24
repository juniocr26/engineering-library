function ownedBox(mode = "normal", guard = "truthiness") {
    let cached;
    let items = [1];
    let context = { owned: true };
    let constructorCalls = 0;
    function ownedFinalize(value) {
        if (mode === "finalizer-throws")
            throw new Error("owned finalizer fault");
        return value;
    }
    class OwnedConstruct {
        rows;
        suppliedContext;
        constructor(rows, suppliedContext) {
            this.rows = rows;
            this.suppliedContext = suppliedContext;
            constructorCalls++;
            if (mode === "constructor-throws")
                throw new Error("owned constructor fault");
        }
    }
    const box = {
        success: false,
        get error() {
            const shouldBuild = guard === "truthiness" ? !cached : cached === undefined;
            if (shouldBuild) {
                cached = new OwnedConstruct(items.map(ownedFinalize), context);
                items = undefined;
                context = undefined;
            }
            return cached;
        },
        set error(value) {
            cached = value;
            items = undefined;
            context = undefined;
        },
    };
    return {
        box,
        inspect() { return { constructor_calls: constructorCalls, items_cleared: items === undefined, context_cleared: context === undefined }; },
    };
}
const results = [];
{
    const h = ownedBox();
    const first = h.box.error;
    const second = h.box.error;
    results.push({ id: "initial-two-reads", ...h.inspect(), same_identity: first === second });
}
{
    const h = ownedBox();
    const replacement = new Error("owned replacement");
    h.box.error = replacement;
    results.push({ id: "truthy-setter-before-read", returned_replacement: h.box.error === replacement, ...h.inspect() });
}
{
    const h = ownedBox();
    h.box.error = 0;
    let thrownName = null;
    try {
        void h.box.error;
    }
    catch (e) {
        thrownName = e.name;
    }
    results.push({ id: "falsy-setter-before-read", thrown_name: thrownName, ...h.inspect() });
}
for (const mode of ["constructor-throws", "finalizer-throws"]) {
    const h = ownedBox(mode);
    let thrownName = null;
    try {
        void h.box.error;
    }
    catch (e) {
        thrownName = e.name;
    }
    results.push({ id: mode, thrown_name: thrownName, ...h.inspect() });
}
{
    const h = ownedBox("normal", "undefined-only");
    h.box.error = 0;
    const returnedZero = h.box.error === 0;
    results.push({ id: "falsy-setter-undefined-only-control", returned_zero: returnedZero, ...h.inspect() });
}
globalThis.ownedResults = results;

# JPEG quality: an early fallback is not a lower bound

Experimental source-reviewed correction by Codex; not owner-approved training gold or published application documentation. Frozen source: go-image-optimizer revision `48476de6e4450294b7769ab7af90805100bb21b5`, `backend/internal/infrastructure/imaging/compress/compressor.go`. The original model arms, `gio-quality-caller` and `gio-quality-helpers`, are retained unchanged. Their source packets omitted the numeric constant; this chapter explicitly adds that declaration from the same frozen file.

## The wrapper supplies two arguments

The receiver method `Compressor.jpegQuality` has no explicit input parameters beyond its receiver and returns an integer. Its entire body returns `clampQuality(c.JPEGQuality, DefaultJPEGQuality)`. The receiver's configured field is the first argument; the named constant is the second. The call expression alone does not establish what the helper does with those arguments. It cannot justify describing the second argument as a lower bound or inventing a number for the constant.

The expanded source supplies `DefaultJPEGQuality = 82`. It also shows the constructor initializing the JPEG-quality field from that constant. This evidence supports the numeric default here. It does not retroactively make a model answer with an unsupported number correct under its smaller original packet. The helper-enriched response invented 80, although the number was absent from its selected declarations and the frozen file actually uses a different value.

## The first branch bypasses later limits

The helper declaration is `clampQuality(value, fallback int) int`. Its first condition is `value == 0`, which returns `fallback` immediately. No later condition is evaluated along that path. The fallback parameter is therefore an alternative result for one sentinel input. The helper does not recursively validate it, compare it to the upper limit or rewrite it through its later branches.

This ordering defeats a tempting but incorrect summary: every possible result of the generic helper lies between 1 and 100. A zero first argument returns the second argument even when that argument falls outside that range. This is a source-derived consequence of the early return, not an observed codec run. The JPEG wrapper supplies a known in-range constant, but that caller-specific fact must remain separate from the contract of the helper for arbitrary arguments.

## The remaining comparisons preserve endpoints

After the zero case, `value < 1` returns `1`. Because zero already returned, this branch covers negative integer inputs on the remaining path. Next, `value > 100` returns `100`. The final statement returns `value` unchanged. Inputs at the two endpoints do not satisfy either strict inequality, so they reach that unchanged-value return. Saying the fallback is the minimum permitted quality would lose both the zero-only sentinel behavior and the lower-bound branch.

The helper response did contain a correct subfact describing the zero, lower, upper and unchanged cases. Other facts in the same answer invented the default and generalized the range incorrectly. The structural writer also refused a helper-owned citation that described the caller. A correct subfact can be preserved as a candidate without approving the whole response or assuming that schema validation establishes factual accuracy.

## Scope ends before encoding behavior

The related methods `Compressor.webpQuality`, `Compressor.avifQuality` and `Compressor.heifQuality` use the same helper with their own receiver fields and named defaults. The file declares defaults of 82 for WebP and 60 for AVIF and HEIF. That parallel call structure supports a family-level source observation; it does not establish that the corresponding encoders interpret the numbers identically or produce equal visual quality.

The inspected quality helper has no image input, error result, codec call or byte-size comparison. It does not prove a compression ratio, smaller output, preservation of metadata or successful decoding. A nearby source comment states an intention about visual similarity and size reduction for JPEG, but intention is not a measured runtime result. The application was not executed. This chapter corrects argument roles, constant provenance and branch boundaries while leaving encoder and imported-helper behavior outside its proof. EN/PT review remains separate from owner approval and any future decision to create training data.

# Static image dimensions: delegation, guards and arithmetic

Codex-authored source-reviewed experimental draft; human approval and publication are pending. Source: go-image-optimizer revision `48476de6e4450294b7769ab7af90805100bb21b5`, `backend/internal/infrastructure/imaging/limits.go`. The actual local-agent baseline and helper arm, `gio-dimensions-caller` and `gio-dimensions-helpers`, remain preserved. The application source was not executed, and this correction is not neural training.

## Two parameters at the wrapper boundary

The declaration `ValidateDimensions(cfg image.Config, maxPixels int) error` receives a configuration object and a pixel budget. It does not receive separate width and height parameters. The body calls `ValidateImageSize(cfg.Width, cfg.Height, maxPixels)` and directly returns its result. Width and height are extracted from the configuration's fields at the call site; the budget is forwarded as the third argument. The wrapper neither reconstructs a configuration nor allocates an image.

This parameter distinction matters because the baseline model invented four inputs: configuration, width, height and maximum pixels. It also confused metadata from the optional source preparer with the application's own contract. Parser metadata can identify a declaration and quote; it does not become another application parameter or establish semantic validation. The wrapper-only excerpt supports reporting delegation and argument expressions. The helper body is necessary to explain the validation branches below.

## Invalid dimensions take priority

The helper `ValidateImageSize` accepts width, height and the budget as integers. Its first condition is `width <= 0 || height <= 0`. Either nonpositive dimension leads immediately to `imageprocessing.ErrInvalidImage`. Both dimensions need to be positive to pass this guard. The logical operator means that one invalid dimension is enough; requiring both to be invalid would change the contract.

This early return also determines the order of arithmetic. The helper does not evaluate its later division when either dimension has already failed the first guard. In particular, the written height used as a divisor is positive on the path that reaches the second condition. That is a local control-flow observation, not a proof about imported error identities or the correctness of an image decoder. The helper examines integers supplied by its caller; it does not parse encoded image bytes.

## The budget comparison is strict

The second condition is `width > maxPixels/height`. If true, the helper returns `imageprocessing.ErrImageTooLarge`. If false, the final result is `nil`. The comparison is strict: equality with the integer quotient does not take this error branch. Describing the condition as greater than or equal would reject an additional boundary. The code expresses division instead of multiplying width by height, so an explanation should preserve the written arithmetic rather than introduce an unchecked product as the implementation.

The body contains no separate positivity check for the budget. This omission does not mean that all budget values succeed; it means their effect follows the existing integer division and comparison. For a positive width and height with a zero budget, the quotient is zero and the strict comparison fails validation. This chapter does not generalize the function into a complete numeric-policy specification or infer constraints that a caller might impose elsewhere.

## A named default is not an automatic wrapper default

The file declares `DefaultMaxDecodedPixels` as `32_000_000`. Its comment motivates the bound using decoded-memory growth and an approximate RGBA example. The static wrapper, however, uses the budget supplied by its caller. It does not select that named default internally. Other functions in the same file can choose it explicitly; sharing a file does not make it an implicit parameter value for every call.

The helper-enriched neural response mentioned positive dimensions, but omitted the exact division, distinct error paths and normal nil return. It also placed helper behavior under the caller's separate citation. The corrected evidence therefore preserves both declarations and their own locations. Successful source selection and literal-citation checking do not prove that a generated explanation preserves parameter roles, early returns or boundary operators. This chapter is a reviewed candidate for later human approval, with no claim about actual decoder execution, memory consumption or network behavior.

## Engineer FAQ

<!-- reading-section: faq:wrapper-parameters -->
### Does the wrapper take width and height as separate parameters?

It receives a configuration and a pixel budget. It extracts the width and height fields when calling the helper. Parser metadata and those argument expressions do not add parameters to the wrapper's declaration.

<!-- reading-section: faq:quotient-equality -->
### Is equality with the integer budget quotient rejected?

The written comparison is strictly greater than. After positive dimensions pass the earlier guard, equality with the quotient avoids that error branch. Nonpositive dimensions return their own earlier error before division.

<!-- reading-section: faq:explicit-budget-argument -->
### Does the static wrapper automatically use the named default?

It forwards its caller's budget unchanged. The named default is a separate declaration. The [animation validator](../go-image-animation/en.md) explicitly selects that static default before its different aggregate check; those choices must not be merged.

The budget concerns pixels, not encoded bytes or an exact resident-memory cap. Decoder validity, imported error identities and observed memory use remain outside this source review.

# Frontend resize dimensions: calculation and error messages are separate

Source-reviewed experimental correction by Codex, pending human approval. Frozen source: go-image-optimizer revision `48476de6e4450294b7769ab7af90805100bb21b5`, `frontend/app/components/image-resize/resize-options.ts`. The actual local-model baseline is `go-image-optimizer-dimensionerror`. Its packet contained only `dimensionError`; this correction explicitly adds `targetDimensions` and the type declarations from the same file. No browser, external application or image operation was executed.

## The data roles at the function boundary

The type `ImageInfo` describes original-image fields including dimensions and a frame count. The type `ResizeOptions` describes a mode, dimension strings, a selected axis, a numeric reduction and an aspect-ratio flag. These declarations describe intended data shapes. They do not add runtime checks to the shown function bodies or prove that every caller supplies valid objects.

The function `targetDimensions` receives those two objects and calculates a candidate result. It initially assigns `Number(options.width)` and `Number(options.height)` to local variables. This conversion occurs before deciding whether the pixel-mode guard applies. Reading the two strings is therefore distinct from deciding whether either converted value passes the later condition. There is no image decoder or network request in this function.

## Pixel-mode validation has an explicit scope

The first return guard is conditional on `options.mode === "pixels"`. Within that mode, it invokes the safe-integer predicate over both local values and compares each with the lower and upper limits. Failure of any listed dimension condition returns `null`. The upper bound used for each entered dimension is 32 million; it is not the same check as the later product budget.

Both entered dimensions are examined by this guard even when subsequent aspect-ratio calculation will derive one dimension from the other. The source does not move validation inside the selected-axis branch. Conversely, this guard is not applied merely because a reduction value exists: its outer mode comparison matters. A description that treats it as universal validation for all modes loses a control-flow condition.

## Scaling occurs after the initial guard

The scaling block is selected by `options.mode === "percentage" || options.keepAspectRatio`. It starts with `(100 - options.reduction) / 100`. When the mode is pixels, it replaces that scale using either the entered height divided by original height or entered width divided by original width, according to the selected axis. Both output dimensions are then calculated from the original dimensions, rounded and passed through a minimum-one expression.

The function finally returns `{ width, height }`. The body contains no separate range check for the reduction and no complete validation of the original image-info object. The presence of rounding and a minimum expression does not establish that every arbitrary runtime input produces a finite, valid size. This chapter records the calculation and guards rather than promising successful resizing or server enforcement.

## The error-message function does not repeat those checks

The function `dimensionError` receives image information and a candidate annotated with `ReturnType<typeof targetDimensions>`. Its first condition is `!target`, returning the message about entering positive whole numbers. That message describes guidance for the user. The condition itself checks the candidate's falsiness; it does not examine either dimension for positivity or integrality.

The next guard compares `target.width * target.height > 32_000_000`. Its true branch returns the static output-limit message. The following guard compares `target.width * target.height * info.frameCount > 64_000_000`, returning the animation-work-limit message. Both comparisons are strict. Equality does not satisfy the corresponding greater-than condition, and the static check is reached before the aggregate frame-work check.

If none of those guards returns, the final result is `null`. The shown function returns strings or that final value; it does not throw the message as an exception. It also does not parse dimension strings or call the calculation function. The annotation expresses a type relationship, while the actual body remains the three ordered guards and final return.

## What changed in this correction

The neural baseline recognized the two numeric thresholds and final null, but attributed positive-integer validation directly to the message function. The standalone syntax producer now adds an optional packet that preserves all three conditions and their exact returned expressions, while keeping its earlier first-guard paragraph unchanged. This is deterministic source evidence, not a model-weight improvement or a new production JavaScript writer. The expanded chapter separates calculation, mode-specific validation and error reporting. Its source, bilingual review and approval status remain explicit; no output was published or promoted into training gold.

## Engineer FAQ

<!-- reading-section: faq:error-message-versus-validation -->
### Does dimensionError itself parse and validate both entered strings?

It receives a candidate and first checks its falsiness. The positive-whole-number message is not a separate dimension-validation algorithm. String conversion and the pixel-mode safe-integer guard belong to the calculation function.

<!-- reading-section: faq:aspect-ratio-validation-order -->
### Can aspect-ratio mode ignore an invalid entered dimension before validation?

In pixel mode, both entered dimensions pass through the initial guard before the later axis-specific scale calculation. That ordering remains relevant even when one final dimension will be derived from the other.

<!-- reading-section: faq:pixel-boundary-and-message-return -->
### Are equal pixel limits rejected or messages thrown as exceptions?

Both product checks use strictly greater than. Equality alone does not take those branches. The function returns its message strings or null; no throw appears in this selected body. Full runtime input validity and backend enforcement require separate evidence.

The [backend dimension validator](go-image-dimensions.md) and [animation validator](go-image-animation.md) are separate contracts. Matching threshold numbers do not prove identical arithmetic, validation order or a complete frontend-to-server integration.

# Configuration loading: defaults, validation and returned values

Source-reviewed experimental draft by Codex, not a neural-model improvement or owner-approved publication. Frozen source: go-image-optimizer revision `48476de6e4450294b7769ab7af90805100bb21b5`, `backend/internal/config/config.go`. The paired local-agent responses are preserved as `gio-configuration-caller` and `gio-configuration-helpers` in the private continuation workspace. Neither complete response was approved.

## The public result and the local candidate

The declaration `Load() (Config, error)` has no input parameters and returns a configuration value together with an error. The configuration type has one exported string field, `Port`. The loader first creates a local candidate and sets its port through `getEnv("PORT", "8080")`. It then passes that candidate's port to the package-local validation helper. Configuration construction and successful configuration return are separate steps: having filled the local field does not mean the caller will receive it.

The failure branch returns `Config{}, err`. That first result is a zero configuration, rather than the locally populated candidate. This distinction corrects the caller-only model draft, which described returning the loaded configuration with an error. A consumer must inspect the error before treating the returned value as usable. The success path instead returns `cfg, nil`, preserving the port string stored in the local candidate. The loader does not replace that string with the parsed integer from validation.

## What the environment helper actually selects

The helper `getEnv` accepts an environment-variable key and a fallback string. Its local value comes from `os.Getenv(key)`. The explicit decision is `value == ""`: when true, it returns the fallback; otherwise, it returns the value. Thus, this implementation does not distinguish an absent variable from a variable whose obtained value is an empty string. Both reach the same branch. In this call site, that branch supplies the default port string.

An obtained nonempty string is returned unchanged by this helper. There is no trimming, integer parsing, case conversion or rewriting here. A string containing spaces is not the empty string, so it is passed onward to validation. The helper therefore selects a candidate; it does not establish that the candidate is a valid port. Details of environment lookup itself belong to the imported standard-library operation, whose implementation is outside this source excerpt.

## Validation preserves two distinct failure paths

The helper `validatePort` receives the selected string. It first calls `strconv.Atoi(port)` and checks the returned error. When that error is non-nil, it returns a formatted numeric-error message containing `%w`, preserving a wrapped cause. No range check is reached along that branch. The source does not define an independent numeric grammar; the imported conversion operation is responsible for parsing. This chapter therefore does not infer acceptance of every possible spelling of an integer.

When parsing reports success, the next guard is `number < 1 || number > 65535`. Either condition produces the range-error message. The endpoints are inclusive: an integer equal to either boundary does not satisfy this guard. The helper finally returns `nil` when neither error path is taken. These are validation results, not a listener allocation, socket bind or proof that a network service can use the port. There is no network startup in this file.

## Address construction and evidence boundaries

The method `Config.Addr` delegates to `net.JoinHostPort("", c.Port)` and returns that call's result. The written host argument is empty and the written port argument is the receiver's stored field. This method does not call the loader or validator. A configuration constructed through some other path can therefore reach this method without passing the validation shown above. The body alone does not prove successful server binding or availability of the requested port.

The helper-enriched model draft gained separate helper citations and the valid numeric range, but omitted the empty-value fallback, conversion-error path and exact loader returns. It also repeated one helper fact three times. More supplied source improved some coverage without establishing a complete explanation. This corrected chapter uses the whole supplied file to keep selection, validation, returned values and address construction distinct. Source was read and parsed; the external application was not executed. Human factual and bilingual approval remains pending.

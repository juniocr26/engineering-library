# sdk-go — Payload encoding

Temporary reviewed partial model excerpt. Important contracts remain undocumented. Not approved for publication; source quotes and full review evidence are preserved separately.

Source revision: `7e0d845246d36fc7f62ade2af885554f94c29db9`.

## 1

The ToPayload function supports converting a single value to a payload by checking if the value is of type RawValue. If it is, the function returns the payload of the RawValue. If not, it iterates over the ordered encodings and tries to convert the value using each payload converter. If none of the converters can convert the value, the function returns an error.

Source: `converter/composite_data_converter.go:83`; SHA-256: `a2f7911b9b9785e00991b8571c364365ee1bb8a649d5ba41bdfef737af05b618`.

    // ToPayload converts single value to payload.
    func (dc *CompositeDataConverter) ToPayload(value any) (*commonpb.Payload, error) {
    	rawValue, ok := value.(RawValue)
    	if ok {
    		return rawValue.Payload(), nil
    	}
    
    	for _, enc := range dc.orderedEncodings {
    		payloadConverter := dc.payloadConverters[enc]
    		payload, err := payloadConverter.ToPayload(value)
    		if err != nil {
    			return nil, err
    		}
    		if payload != nil {
    			return payload, nil
    		}
    	}
    
    	return nil, fmt.Errorf("value: %v of type: %T: %w", value, value, ErrUnableToFindConverter)
    }



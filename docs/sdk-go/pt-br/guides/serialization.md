# sdk-go — Codificação de payloads

Trecho parcial temporário do modelo, revisado. Contratos importantes continuam sem documentação. Sem aprovação de publicação; citações do código e evidências completas da revisão ficam preservadas separadamente.

Revisão de origem: `7e0d845246d36fc7f62ade2af885554f94c29db9`.

## 1

A função ToPayload suporta a conversão de um valor para um payload ao verificar se o valor é do tipo RawValue. Se for, a função retorna o payload do RawValue. Se não for, ela itera sobre as codificações ordenadas e tenta converter o valor usando cada conversor de payload. Se nenhum dos conversores pode converter o valor, a função retorna um erro.

Fonte: `converter/composite_data_converter.go:83`; SHA-256: `a2f7911b9b9785e00991b8571c364365ee1bb8a649d5ba41bdfef737af05b618`.

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



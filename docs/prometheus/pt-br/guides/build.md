# prometheus — Requisitos do módulo Go

Trecho parcial temporário do modelo, revisado. Contratos importantes continuam sem documentação. Sem aprovação de publicação; citações do código e evidências completas da revisão ficam preservadas separadamente.

Revisão de origem: `b2a602494b65bda38316eabaef7e0d834a6814dd`.

## 1

O código define uma pasta de módulo Go com uma lista de dependências, incluindo bibliotecas do Azure e outras bibliotecas. Isso suporta o uso dessas bibliotecas em um projeto Go.

Fonte: `go.mod:1`; SHA-256: `eaf45811931ab08ff878bb9942f6077d4650585e35e33e7a9ea6f2920e9a168b`.

    module github.com/prometheus/prometheus
    
    go 1.26.10
    
    require (
    	github.com/Azure/azure-sdk-for-go/sdk/azcore v1.23.3
    	github.com/Azure/azure-sdk-for-go/sdk/azidentity v1.15.0
    	github.com/Azure/azure-sdk-for-go/sdk/resourcemanager/compute/armcompute/v8 v8.4.0
    	github.com/Azure/azure-sdk-for-go/sdk/resourcemanager/network/armnetwork/v8 v8.0.0
    	github.com/Code-Hex/go-generics-cache v1.5.1
    	github.com/KimMachineGun/automemlimit v1.0.0
    	github.com/alecthomas/kingpin/v2 v2.4.0
    	github.com/alecthomas/units v0.0.0-20240927000941-0f3dac36c52b
    	github.com/aws/aws-sdk-go-v2 v1.47.4
    	github.com/aws/aws-sdk-go-v2/config v1.33.9



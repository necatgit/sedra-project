// Prints Sedra address test vectors from the Go implementation (sedrad v2.0.0, 4a1153d), used to cross-check
// rusty-kaspa's address tests. Run from a sedrad checkout as cmd/zz_addrvectors/main.go: go run ./cmd/zz_addrvectors
package main

import (
	"encoding/hex"
	"fmt"

	"github.com/sedracoin/sedrad/util"
)

func must(a util.Address, err error) string {
	if err != nil {
		panic(err)
	}
	return a.EncodeAddress()
}

func main() {
	z32, z33 := make([]byte, 32), make([]byte, 33)
	e, _ := hex.DecodeString("ba01fc5f4e9d9879599c69a3dafdb835a7255e5f2e934e9322ecd3af190ab0f60e")
	m, _ := hex.DecodeString("5fff3c4da18f45adcdd499e44611e9fff148ba69db3c4ea2ddd955fc46a59522")
	fmt.Println(must(util.NewAddressPublicKey(z32, util.Bech32PrefixSedraTest)))
	fmt.Println(must(util.NewAddressPublicKeyECDSA(z33, util.Bech32PrefixSedraTest)))
	fmt.Println(must(util.NewAddressPublicKeyECDSA(e, util.Bech32PrefixSedraTest)))
	fmt.Println(must(util.NewAddressPublicKey(z32, util.Bech32PrefixSedra)))
	fmt.Println(must(util.NewAddressPublicKey(m, util.Bech32PrefixSedra)))
}

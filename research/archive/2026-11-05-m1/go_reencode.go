// Re-encodes Kaspa addresses (stdin, one per line) with Sedra prefixes using sedrad's own bech32 code (v2.0.0, 4a1153d).
// Output: "<kaspa address> <sedra address>". Produced address-reencode-map.txt (347 addresses from rusty-kaspa tests).
// Run from a sedrad checkout as cmd/zz_reencode/main.go: go run ./cmd/zz_reencode < addresses.txt
package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"github.com/sedracoin/sedrad/util/bech32"
)

func main() {
	m := map[string]string{"kaspa": "sedra", "kaspatest": "sedratest", "kaspasim": "sedrasim", "kaspadev": "sedradev"}
	sc := bufio.NewScanner(os.Stdin)
	for sc.Scan() {
		a := strings.TrimSpace(sc.Text())
		prefix, payload, version, err := bech32.Decode(a)
		if err != nil {
			fmt.Fprintln(os.Stderr, "DECODE-ERROR", a, err)
			os.Exit(1)
		}
		fmt.Printf("%s %s\n", a, bech32.Encode(m[prefix], payload, version))
	}
}

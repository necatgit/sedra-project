package zzrelaunch

// Temporary generator (not part of sedrad): calls sedrad v2.0.0's own difficulty-reset and treasury-allocation code
// with mainnet params for DAA scores around every window boundary, to cross-check the Rust node.
// Run: RELAUNCH_VECTORS_OUT=out.json go test ./domain/consensus/processes/zzrelaunch -run TestZZRelaunchVectors

import (
	"encoding/hex"
	"encoding/json"
	"os"
	"sort"
	"testing"

	"github.com/sedracoin/sedrad/domain/consensus/model"
	"github.com/sedracoin/sedrad/domain/consensus/model/externalapi"
	"github.com/sedracoin/sedrad/domain/consensus/processes/coinbasemanager"
	"github.com/sedracoin/sedrad/domain/consensus/processes/difficultymanager"
	"github.com/sedracoin/sedrad/domain/dagconfig"
)

type store struct {
	model.DAABlocksStore
	score uint64
}

func (s *store) DAAScore(model.DBReader, *model.StagingArea, *externalapi.DomainHash) (uint64, error) {
	return s.score, nil
}

func TestZZRelaunchVectors(t *testing.T) {
	out := os.Getenv("RELAUNCH_VECTORS_OUT")
	if out == "" {
		t.Skip("RELAUNCH_VECTORS_OUT not set")
	}
	p := dagconfig.MainnetParams
	st := &store{}
	cm := coinbasemanager.ZZNewForVectors(&p, st)
	dm := difficultymanager.ZZNewForVectors(&p, st)
	nonGenesis := externalapi.NewDomainHashFromByteArray(&[externalapi.DomainHashSize]byte{1})
	const computedBits = uint32(0x1b0fffff) // an arbitrary "normal" result of the difficulty calculation

	set := map[uint64]bool{0: true, 1: true, 53_000_000: true, 61_000_000: true}
	add := func(b uint64) { set[b-1], set[b], set[b+1] = true, true, true }
	add(p.DifficultyResetActivationDaaScore)
	add(p.DifficultyResetActivationDaaScore + p.DifficultyResetWindowBlocks)
	for i := range p.TreasuryAllocationActivationDaaScore {
		add(p.TreasuryAllocationActivationDaaScore[i])
		add(p.TreasuryAllocationActivationDaaScore[i] + p.TreasuryAllocationWindowBlocks[i])
		set[p.TreasuryAllocationActivationDaaScore[i]+p.TreasuryAllocationWindowBlocks[i]/2] = true
	}
	set[(p.TreasuryAllocationActivationDaaScore[0]+p.TreasuryAllocationWindowBlocks[0]+p.TreasuryAllocationActivationDaaScore[1])/2] = true
	scores := []uint64{}
	for d := range set {
		scores = append(scores, d)
	}
	sort.Slice(scores, func(i, j int) bool { return scores[i] < scores[j] })

	type vec struct {
		DaaScore       uint64  `json:"daa_score"`
		Bits           uint32  `json:"bits_after_reset"`
		TreasuryValue  *uint64 `json:"treasury_value"`
		TreasuryScript *string `json:"treasury_script"`
	}
	vecs := []vec{}
	for _, d := range scores {
		st.score = d
		bits, err := dm.ZZApplyDifficultyReset(nonGenesis, computedBits)
		if err != nil {
			t.Fatal(err)
		}
		v := vec{DaaScore: d, Bits: bits}
		o, ok, err := cm.ZZTreasuryAllocationOutput(nonGenesis)
		if err != nil {
			t.Fatal(err)
		}
		if ok {
			val := o.Value
			s := hex.EncodeToString(o.ScriptPublicKey.Script)
			v.TreasuryValue, v.TreasuryScript = &val, &s
		}
		vecs = append(vecs, v)
	}
	doc := map[string]interface{}{
		"source":        "sedrad v2.0.0 (4a1153d): difficultyManager.applyDifficultyReset and coinbaseManager.treasuryAllocationOutput, MainnetParams",
		"computed_bits": computedBits,
		"genesis_bits":  p.GenesisBlock.Header.Bits(),
		"vectors":       vecs,
	}
	b, _ := json.MarshalIndent(doc, "", " ")
	if err := os.WriteFile(out, b, 0o644); err != nil {
		t.Fatal(err)
	}
	t.Logf("wrote %d vectors", len(vecs))
}

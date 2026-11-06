package coinbasemanager

// Temporary generator (not part of sedrad): prints Sedra mainnet block subsidies computed by sedrad's own
// CalcBlockSubsidy, for cross-checking the Rust node. Only the DAA score lookup is stubbed.
// Run: SUBSIDY_VECTORS_OUT=/path/out.json go test ./domain/consensus/processes/coinbasemanager -run TestZZSubsidyVectors

import (
	"encoding/json"
	"os"
	"sort"
	"testing"

	"github.com/sedracoin/sedrad/domain/consensus/model"
	"github.com/sedracoin/sedrad/domain/consensus/model/externalapi"
	"github.com/sedracoin/sedrad/domain/dagconfig"
)

type zzDaaStore struct {
	model.DAABlocksStore
	score uint64
}

func (s *zzDaaStore) DAAScore(model.DBReader, *model.StagingArea, *externalapi.DomainHash) (uint64, error) {
	return s.score, nil
}

func TestZZSubsidyVectors(t *testing.T) {
	out := os.Getenv("SUBSIDY_VECTORS_OUT")
	if out == "" {
		t.Skip("SUBSIDY_VECTORS_OUT not set")
	}
	p := dagconfig.MainnetParams
	store := &zzDaaStore{}
	c := &coinbaseManager{
		subsidyGenesisReward:            p.SubsidyGenesisReward,
		preDeflationaryPhaseBaseSubsidy: p.PreDeflationaryPhaseBaseSubsidy,
		genesisHash:                     p.GenesisHash,
		deflationaryPhaseDaaScore:       p.DeflationaryPhaseDaaScore,
		deflationaryPhaseBaseSubsidy:    p.DeflationaryPhaseBaseSubsidy,
		daaBlocksStore:                  store,
	}
	nonGenesis := externalapi.NewDomainHashFromByteArray(&[externalapi.DomainHashSize]byte{1})

	const month = uint64(2629800)
	def := p.DeflationaryPhaseDaaScore
	set := map[uint64]bool{0: true, 1: true, 2: true, def - 1: true, def: true, def + 1: true}
	for k := uint64(0); k <= 200; k++ {
		b := def + k*month
		set[b-1], set[b], set[b+1] = true, true, true
		set[b+month/2] = true
	}
	for _, d := range []uint64{61_119_321, 53_625_512, 53_632_372, 53_633_267, def + 1000*month, 1 << 40} {
		set[d] = true
	}
	scores := make([]uint64, 0, len(set))
	for d := range set {
		scores = append(scores, d)
	}
	sort.Slice(scores, func(i, j int) bool { return scores[i] < scores[j] })

	type vec struct {
		DaaScore uint64 `json:"daa_score"`
		Subsidy  uint64 `json:"subsidy"`
	}
	vecs := make([]vec, 0, len(scores))
	for _, d := range scores {
		store.score = d
		s, err := c.CalcBlockSubsidy(nil, nonGenesis)
		if err != nil {
			t.Fatal(err)
		}
		vecs = append(vecs, vec{d, s})
	}
	doc := map[string]interface{}{
		"source":                          "sedrad v2.0.0 (4a1153d), coinbasemanager.CalcBlockSubsidy, MainnetParams",
		"deflationary_phase_daa_score":    def,
		"pre_deflationary_phase_subsidy":  p.PreDeflationaryPhaseBaseSubsidy,
		"vectors":                         vecs,
	}
	b, _ := json.MarshalIndent(doc, "", " ")
	if err := os.WriteFile(out, b, 0o644); err != nil {
		t.Fatal(err)
	}
	t.Logf("wrote %d vectors", len(vecs))
}

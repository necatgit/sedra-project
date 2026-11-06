package difficultymanager

// Temporary test-only export (not part of sedrad) so an external generator can call the unexported reset code.

import (
	"github.com/sedracoin/sedrad/domain/consensus/model"
	"github.com/sedracoin/sedrad/domain/consensus/model/externalapi"
	"github.com/sedracoin/sedrad/domain/dagconfig"
)

type ZZDifficultyManager struct{ d *difficultyManager }

func ZZNewForVectors(p *dagconfig.Params, st model.DAABlocksStore) *ZZDifficultyManager {
	return &ZZDifficultyManager{&difficultyManager{
		genesisBits:                       p.GenesisBlock.Header.Bits(),
		difficultyResetActivationDaaScore: p.DifficultyResetActivationDaaScore,
		difficultyResetWindowBlocks:       p.DifficultyResetWindowBlocks,
		daaBlocksStore:                    st,
	}}
}

func (z *ZZDifficultyManager) ZZApplyDifficultyReset(h *externalapi.DomainHash, bits uint32) (uint32, error) {
	return z.d.applyDifficultyReset(nil, h, bits)
}

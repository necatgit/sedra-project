package coinbasemanager

// Temporary test-only export (not part of sedrad) so an external generator can call the unexported treasury code.

import (
	"github.com/sedracoin/sedrad/domain/consensus/model"
	"github.com/sedracoin/sedrad/domain/consensus/model/externalapi"
	"github.com/sedracoin/sedrad/domain/dagconfig"
)

type ZZCoinbaseManager struct{ c *coinbaseManager }

func ZZNewForVectors(p *dagconfig.Params, st model.DAABlocksStore) *ZZCoinbaseManager {
	return &ZZCoinbaseManager{&coinbaseManager{
		genesisHash:                          p.GenesisHash,
		treasuryAllocationActivationDaaScore: p.TreasuryAllocationActivationDaaScore,
		treasuryAllocationWindowBlocks:       p.TreasuryAllocationWindowBlocks,
		treasuryAllocationPerBlockSeep:       p.TreasuryAllocationPerBlockSeep,
		treasuryScriptPublicKey:              p.TreasuryScriptPublicKey,
		daaBlocksStore:                       st,
	}}
}

func (z *ZZCoinbaseManager) ZZTreasuryAllocationOutput(h *externalapi.DomainHash) (*externalapi.DomainTransactionOutput, bool, error) {
	return z.c.treasuryAllocationOutput(nil, h)
}

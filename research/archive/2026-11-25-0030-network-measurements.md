# Network measurements for SIP-0002 (issue #30), 2026-11-25

Raw evidence behind [SIP-0002](../../proposals/SIP-0002-network-resilience.md) "Where Sedra stands (re-measured
2026-11-25)". Never edited after publication. IP addresses that were not already public are replaced by a label:
this project's public node is "own public node", other outside nodes are "outside node A/B/…". The two fallback
peers' addresses are public in sedrad's source and in QUESTIONS.md Q5.

All commands ran on the project's test VM (the host of the public Rust node and of a local Go node `sedrad-dev`,
v2.0.0, which is not a production node), except the RDAP and GitHub queries (developer PC).

## 1. Network map: how many Sedra nodes accept P2P connections

Script `/data/netmap.sh` (systemd timer every 6 h): asks the local Go node for every address it knows
(`sedractl GetPeerAddresses`) and tries a TCP connect to each one's P2P port (4 s timeout). It counts listening nodes
only; nodes behind NAT are not counted.

```
$ grep -h NETMAP /data/logs/netmap/*.log
2026-11-14T18:36:18Z NETMAP known=4000 open=4
2026-11-15T00:30:06Z NETMAP known=4 open=4
2026-11-15T06:31:37Z NETMAP known=1003 open=4
2026-11-15T12:30:05Z NETMAP known=4 open=4
2026-11-15T18:31:36Z NETMAP known=1001 open=4
2026-11-16T00:30:06Z NETMAP known=4 open=4
2026-11-16T06:30:06Z NETMAP known=4 open=4
2026-11-16T12:30:05Z NETMAP known=4 open=4
2026-11-16T18:31:38Z NETMAP known=1001 open=4
2026-11-17T00:30:05Z NETMAP known=4 open=4
2026-11-17T06:33:39Z NETMAP known=2344 open=4
2026-11-17T12:30:05Z NETMAP known=4 open=4
2026-11-17T18:30:05Z NETMAP known=4 open=4
2026-11-18T00:30:05Z NETMAP known=4 open=4
2026-11-18T06:30:05Z NETMAP known=4 open=4
2026-11-18T12:31:36Z NETMAP known=1006 open=4
2026-11-18T18:34:21Z NETMAP known=2811 open=5
2026-11-19T00:36:21Z NETMAP known=4094 open=5
2026-11-19T06:33:27Z NETMAP known=2204 open=5
2026-11-19T12:34:33Z NETMAP known=2976 open=5
2026-11-19T18:31:16Z NETMAP known=816 open=3
2026-11-20T00:30:05Z NETMAP known=3 open=3
2026-11-20T06:30:05Z NETMAP known=3 open=3
2026-11-20T12:30:02Z NETMAP known=3 open=3
2026-11-20T18:30:01Z NETMAP known=3 open=3
2026-11-21T00:35:49Z NETMAP known=3801 open=5
2026-11-21T06:35:41Z NETMAP known=3702 open=5
2026-11-21T12:30:05Z NETMAP known=4 open=4
2026-11-21T18:30:05Z NETMAP known=4 open=4
2026-11-22T00:30:05Z NETMAP known=4 open=4
2026-11-22T06:30:07Z NETMAP known=4 open=4
2026-11-22T12:30:05Z NETMAP known=4 open=4
2026-11-22T18:31:36Z NETMAP known=1002 open=4
2026-11-23T20:45:17Z NETMAP known=239 open=4
2026-11-24T00:33:25Z NETMAP known=1877 open=4
2026-11-24T06:30:04Z NETMAP known=4 open=4
2026-11-24T12:34:13Z NETMAP known=2680 open=4
2026-11-24T18:30:09Z NETMAP known=4 open=4
2026-11-25T00:30:08Z NETMAP known=4 open=4
2026-11-25T06:30:12Z NETMAP known=3 open=3
2026-11-25T12:30:01Z NETMAP known=3 open=3
2026-11-25T18:30:06Z NETMAP known=3 open=3
```

(No runs between 2026-11-22 18:31 and 2026-11-23 20:45 UTC: the test VM was down.)

Open addresses on 2026-11-25:

```
2026-11-25T00:30:08Z OPEN <outside node A>:22111
2026-11-25T00:30:08Z OPEN 169.58.111.191:22111
2026-11-25T00:30:08Z OPEN 169.58.126.141:22111
2026-11-25T00:30:08Z OPEN <own public node>:22111
2026-11-25T06:30:12Z OPEN 169.58.111.191:22111
2026-11-25T06:30:12Z OPEN 169.58.126.141:22111
2026-11-25T06:30:12Z OPEN <own public node>:22111
(12:30 and 18:30 UTC: the same three)
```

Reading (Inferred): "known" jumps between a handful and thousands because the Go node learns large batches of
gossiped addresses that are not reachable and drops them again after four failed attempts (section 4). "open" has been
3 to 5 since 2026-11-14. On 2026-11-25 the only reachable nodes were the two fallback peers and this project's node.

## 2. DNS seeders

```
$ for s in 1 2 3; do dig +short sedra-seed-$s.sedracoin.com A; dig +short sedra-seed-$s.sedracoin.com AAAA; dig +short sedra-seed-$s.sedracoin.com NS; done
== sedra-seed-1 2026-11-25T21:57:19Z
169.58.111.191
== sedra-seed-2 2026-11-25T21:57:19Z
== sedra-seed-3 2026-11-25T21:57:19Z

$ dig sedra-seed-2.sedracoin.com A | grep -E "status|ANSWER"
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 36568
;; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

$ dig +short @1.1.1.1 / @8.8.8.8 sedra-seed-N.sedracoin.com A   (both resolvers the same)
seed-1: 169.58.111.191  ttl=3600
seed-2: (empty)
seed-3: (empty)
```

Reading (Verified): seed-1 is a fixed A record (one address, TTL 3600, no NS delegation to a seeder program);
seed-2 and seed-3 exist (NOERROR) but return no address. None of the three behaves like a crawling DNS seeder, which
answers with many current node addresses. (The authoritative name servers of sedracoin.com did not answer a direct
query from the test VM; the public resolvers above did.)

## 3. Fallback peers

```
$ git -C sedrad grep -n -i "fallbackpeer\|169\.58" origin/relaunch/v2.0.0 -- '*.go'    # 4a1153d8
domain/dagconfig/params.go:77:	// DefaultFallbackPeers is a list of hardcoded bootstrap peers (host:port)
domain/dagconfig/params.go:83:	DefaultFallbackPeers []string
domain/dagconfig/params.go:261:	// DefaultFallbackPeers are our operated bootstrap nodes, used only when the
domain/dagconfig/params.go:266:	DefaultFallbackPeers: []string{
domain/dagconfig/params.go:267:		"169.58.126.141", // hub node
domain/dagconfig/params.go:268:		"169.58.111.191", // secondary node
infrastructure/config/config.go:537:		cfg.AddPeers = append(cfg.AddPeers, cfg.NetParams().DefaultFallbackPeers...)

$ git -C sedra-rusty grep -n -i "fallback_peer\|169\.58\|fallback peer" origin/dev -- '*.rs'    # 00757c4e
(no output)
```

config.go:530-538: the Go node adds the fallback peers as permanent peers only when neither `--addpeer` nor
`--connect` is given. The Rust node has no fallback peers; it has only the three DNS seeders
(`consensus/core/src/config/params.rs:520-525` on `dev`).

```
$ curl -s https://rdap.db.ripe.net/ip/169.58.111.191   (and .126.141; 2026-11-25 22:01 UTC)
169.58.111.191 169.58.0.0 - 169.58.127.255 TT-20260630 DE ['MH7476-RIPE', 'MNT-CONTABO', 'ORG-CG316-RIPE', 'MH12453-RIPE']
169.58.126.141 169.58.0.0 - 169.58.127.255 TT-20260630 DE ['MH7476-RIPE', 'MNT-CONTABO', 'ORG-CG316-RIPE', 'MH12453-RIPE']
```

Reading (Verified): both fallback peers are in the same /17 of one hosting provider; seed-1 points at one of them.

## 4. Address book and peer selection in the code

| | Go sedrad `relaunch/v2.0.0` (`4a1153d8`) | Rust sedra-rusty `dev` (`00757c4e`) |
|---|---|---|
| Stored per address | address + `connectionFailedCount` (`infrastructure/network/addressmanager/addressmanager.go:34-37`) | address + `connection_failed_count` (`components/addressmanager/src/stores/address_store.rs:16-19`) |
| Size limit | 4096 (`addressmanager.go:19`) | 4096 (`components/addressmanager/src/lib.rs:27`) |
| New address | count 1 until the first success (`addressmanager.go:92-93`) | count 1 until the first success (`lib.rs:264-265`) |
| Forgotten | at 4 failures (`addressmanager.go:20, 165-169`) | above 3 failures (`lib.rs:28, 273-276`) |
| Outbound choice | random among not-banned addresses (`connmanager/outgoing_connections.go:34`, `addressmanager.go:215-219`; weighting by failure count in `NewAddressRandomize`) | random, weight 64^(4-failures), spread over IP prefix buckets (`lib.rs:413-450`) |
| Outbound target / inbound limit | 8 / 117 (`infrastructure/config/config.go:36-37`) | 8 / 128 (`kaspad/src/args.rs:107-108`) |
| DNS seeders asked | when the address book cannot fill the target (`outgoing_connections.go:55-59`) | when missing > 0; all seeders if more than half the target is missing (`connectionmanager/src/lib.rs:235-243`) |
| Last seen, uptime, preferred peers | none | none |

Reading (Verified from the code above): a node that is unreachable for three or four connection attempts is deleted
from every address book that tried it. A public node that is down for a few hours can be forgotten by the network and
comes back only through new gossip.

## 5. The public Rust node's peers

```
$ journalctl -u sedra-rusty --since "2026-11-18 22:00"   (counted by a script, 2026-11-25 ~21:58 UTC)
inbound distinct IPs since 11-18 22:00: 12
inbound connections: 50
outbound distinct: 127.0.0.1 169.58.111.191 <outside node A> [::ffff:169.58.126.141]
inbound distinct last 24h: 4
max inbound gauge: 11
ActiveEnterTimestamp=Tue 2026-11-24 06:58:46 UTC
```

Last log lines (2026-11-25 21:42 and 21:58 UTC): "P2P Connected to incoming peer … (inbound: 5)" and "(inbound: 6)".
127.0.0.1 is the local Go node on the same VM (configured with `--addpeer`). Reading (Verified): the public node
still gets inbound peers (6 at 21:58 UTC); for outbound it finds only three outside nodes, because there are no more
reachable ones.

## 6. Upstream rusty-kaspa and Bitcoin Core (checked 2026-11-25)

```
$ gh api repos/kaspanet/rusty-kaspa/commits/master --jq '.sha+" "+.commit.committer.date'
68bd2e91cddbdcdca5e59357344c7e26f2d6d97b 2026-11-23T15:55:13Z
$ gh api repos/kaspanet/rusty-kaspa/contents/components/addressmanager/src/stores/address_store.rs --jq .content | base64 -d | grep -A3 "pub struct Entry"
pub struct Entry {
    pub connection_failed_count: u64,
    pub address: NetAddress,
}
$ gh api repos/kaspanet/rusty-kaspa/pulls/796 --jq '"#\(.number) \(.state) merged=\(.merged_at) created=\(.created_at) updated=\(.updated_at) \(.title)"'
#796 open merged=null created=2025-12-25T21:59:33Z updated=2026-05-06T10:02:24Z P2P / Networking — Implementation of Perigee p2p Routing.
$ gh api repos/kaspanet/rusty-kaspa/pulls/812 ...
#812 open merged=null created=2026-01-10T07:37:41Z updated=2026-05-06T10:03:03Z Address Manager / Args: Add `--reset-address-stores` flag and functionality.
```

#796 (not merged, no reviews, merge state "dirty") adds a separate persisted store of ranked "perigee" peers
(`PerigeeEntry { rank: u16, address }`), a `--blk-perigee-persist` flag, and a priority list in front of the random
choice (`iterate_prioritized_random_addresses(priorities, exceptions)`, `RandomWeightedIteratorWithPriorities`).
Perigee chooses peers by how fast they deliver blocks; it does not keep last-seen times or protect good peers from
being forgotten.

Bitcoin Core `master` (`0e8f70a863`): `src/net.cpp:73` `MAX_BLOCK_RELAY_ONLY_ANCHORS = 2`; `anchors.dat` written at
shutdown (`net.cpp:3829`) and read at start (`net.cpp:3659`), anchors get the highest priority for block-relay-only
connections (`net.cpp:2812`). Its address manager stores per address `m_last_try`, `m_last_success`, `nAttempts`
(`src/addrman_impl.h:49-61`) and keeps addresses in bucketed "new" and "tried" tables (`addrman_impl.h:26-30`).

```
$ gh search repos "sedra dnsseeder"           → []
$ gh api users/sedracoin/repos --jq '.[].name' → no seeder repository
$ gh api repos/kaspanet/dnsseeder --jq '"\(.full_name) \(.pushed_at) \(.language)"'
kaspanet/dnsseeder 2025-11-19T23:44:23Z Go
```

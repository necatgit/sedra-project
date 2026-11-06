"""Hardening 3: bounded, concurrent inbound P2P handshakes (upstream rusty-kaspa 2a47b249, part). Run from repo root."""
import pathlib


def edit(path, pairs):
    p = pathlib.Path(path)
    s = p.read_text()
    for old, new in pairs:
        assert s.count(old) == 1, f"{path}: expected 1 occurrence of {old[:70]!r}, found {s.count(old)}"
        s = s.replace(old, new)
    p.write_text(s)
    print("ok", path)


# ---------- router: is_closed ----------
edit("protocol/p2p/src/core/router.rs", [(
    "    /// Indicates whether this connection is an outbound connection\n    pub fn is_outbound(&self) -> bool {\n        self.is_outbound\n    }\n",
    "    /// Indicates whether this connection is an outbound connection\n    pub fn is_outbound(&self) -> bool {\n        self.is_outbound\n    }\n\n"
    "    /// SEDRA (security back-port, upstream rusty-kaspa 2a47b249): true once `close()` has run\n"
    "    pub(crate) fn is_closed(&self) -> bool {\n        self.mutable_state.lock().shutdown_signal.is_none()\n    }\n",
)])

# ---------- adaptor: hub no longer needs the initializer ----------
p = pathlib.Path("protocol/p2p/src/core/adaptor.rs")
s = p.read_text()
assert s.count("adaptor.hub.clone().start_event_loop(hub_receiver, initializer);") == 2
s = s.replace("adaptor.hub.clone().start_event_loop(hub_receiver, initializer);", "adaptor.hub.clone().start_event_loop(hub_receiver);")
n = s.count("ConnectionHandler::new(hub_sender, initializer.clone(), counters)")
assert n == 2, n
s = s.replace("ConnectionHandler::new(hub_sender, initializer.clone(), counters)", "ConnectionHandler::new(hub_sender, initializer, counters)")
p.write_text(s)
print("ok protocol/p2p/src/core/adaptor.rs")

# ---------- hub: register finished peers only ----------
edit("protocol/p2p/src/core/hub.rs", [
    ("use crate::{common::ProtocolError, pb::KaspadMessage, ConnectionInitializer, Peer, Router};\nuse kaspa_core::{debug, info, warn};",
     "use crate::{common::ProtocolError, pb::KaspadMessage, Peer, Router};\nuse kaspa_core::{debug, info};"),
    ("    pub(crate) fn start_event_loop(self, mut hub_receiver: MpscReceiver<HubEvent>, initializer: Arc<dyn ConnectionInitializer>) {",
     "    pub(crate) fn start_event_loop(self, mut hub_receiver: MpscReceiver<HubEvent>) {"),
    ('''                    HubEvent::NewPeer(new_router) => {
                        // If peer is outbound then connection initialization was already performed as part of the connect logic
                        if new_router.is_outbound() {
                            info!("P2P Connected to outgoing peer {} (outbound: {})", new_router, self.peers_query(true) + 1);
                            self.insert_new_router(new_router).await;
                        } else {
                            match initializer.initialize_connection(new_router.clone()).await {
                                Ok(()) => {
                                    info!("P2P Connected to incoming peer {} (inbound: {})", new_router, self.peers_query(false) + 1);
                                    self.insert_new_router(new_router).await;
                                }
                                Err(err) => {
                                    new_router.try_sending_reject_message(&err).await;
                                    // Ignoring the new router
                                    new_router.close().await;
                                    if matches!(err, ProtocolError::LoopbackConnection(_) | ProtocolError::PeerAlreadyExists(_)) {
                                        debug!("P2P, handshake failed for inbound peer {}: {}", new_router, err);
                                    } else {
                                        warn!("P2P, handshake failed for inbound peer {}: {}", new_router, err);
                                    }
                                }
                            }
                        }
                    }''',
     '''                    HubEvent::NewPeer(new_router) => {
                        // SEDRA (security back-port, upstream rusty-kaspa 2a47b249): connection initialization (the handshake)
                        // has already been performed before the router reaches the hub, for outbound peers by the connect
                        // logic and for inbound peers by a task of their own in the connection handler. The hub no longer
                        // runs handshakes, so one slow peer cannot block all others.
                        // PeerClosing may be handled before NewPeer, so avoid inserting a router that is already closed.
                        if new_router.is_closed() {
                            continue;
                        }
                        let is_outbound = new_router.is_outbound();
                        info!(
                            "P2P Connected to {} peer {} ({}: {})",
                            if is_outbound { "outgoing" } else { "incoming" },
                            new_router,
                            if is_outbound { "outbound" } else { "inbound" },
                            self.peers_query(is_outbound) + 1
                        );
                        self.insert_new_router(new_router).await;
                    }'''),
])
s = pathlib.Path("protocol/p2p/src/core/hub.rs").read_text()
if "ProtocolError" not in s.split("impl Hub")[1]:
    s = s.replace("use crate::{common::ProtocolError, pb::KaspadMessage, Peer, Router};", "use crate::{pb::KaspadMessage, Peer, Router};")
    pathlib.Path("protocol/p2p/src/core/hub.rs").write_text(s)
    print("removed unused ProtocolError import from hub.rs")

# ---------- connection handler: guard + spawned inbound handshake ----------
C = "protocol/p2p/src/core/connection_handler.rs"
edit(C, [
    ("use kaspa_core::{debug, info};\n", "use kaspa_core::{debug, info, warn};\nuse parking_lot::Mutex;\nuse std::collections::HashMap;\nuse std::net::IpAddr;\n"),
    ("#[derive(Error, Debug)]\npub enum ConnectionError {",
     '''// SEDRA (security back-port, upstream rusty-kaspa 2a47b249): bound pending inbound handshakes, globally and per source IP
const MAX_PENDING_INBOUND_HANDSHAKES: usize = 32;
const MAX_PENDING_INBOUND_HANDSHAKES_PER_IP: usize = 2;

#[derive(Debug, Default)]
struct PendingInboundHandshakes {
    total: usize,
    by_ip: HashMap<IpAddr, usize>,
}

impl PendingInboundHandshakes {
    fn try_reserve(&mut self, ip: IpAddr) -> bool {
        let ip_count = self.by_ip.get(&ip).copied().unwrap_or_default();
        if self.total >= MAX_PENDING_INBOUND_HANDSHAKES || ip_count >= MAX_PENDING_INBOUND_HANDSHAKES_PER_IP {
            return false;
        }
        self.total += 1;
        self.by_ip.insert(ip, ip_count + 1);
        true
    }

    fn release(&mut self, ip: IpAddr) {
        self.total = self.total.checked_sub(1).expect("a pending inbound handshake reservation must exist");
        let remove = {
            let count = self.by_ip.get_mut(&ip).expect("a pending inbound handshake IP reservation must exist");
            *count = count.checked_sub(1).expect("a pending inbound handshake IP reservation must exist");
            *count == 0
        };
        if remove {
            self.by_ip.remove(&ip);
        }
    }
}

/// Holds one reservation in [`PendingInboundHandshakes`] and releases it when dropped
struct PendingInboundHandshakeGuard {
    pending: Arc<Mutex<PendingInboundHandshakes>>,
    ip: IpAddr,
}

impl PendingInboundHandshakeGuard {
    fn try_new(pending: Arc<Mutex<PendingInboundHandshakes>>, ip: IpAddr) -> Option<Self> {
        if pending.lock().try_reserve(ip) {
            Some(Self { pending, ip })
        } else {
            None
        }
    }
}

impl Drop for PendingInboundHandshakeGuard {
    fn drop(&mut self) {
        self.pending.lock().release(self.ip);
    }
}

#[derive(Error, Debug)]
pub enum ConnectionError {'''),
    ("    initializer: Arc<dyn ConnectionInitializer>,\n    counters: Arc<TowerConnectionCounters>,\n}",
     "    initializer: Arc<dyn ConnectionInitializer>,\n    counters: Arc<TowerConnectionCounters>,\n    pending_inbound_handshakes: Arc<Mutex<PendingInboundHandshakes>>,\n}"),
    ("        Self { hub_sender, initializer, counters }",
     "        Self { hub_sender, initializer, counters, pending_inbound_handshakes: Default::default() }"),
    ('''        // Build the in/out pipes
        let (outgoing_route, outgoing_receiver) = mpsc_channel(Self::outgoing_network_channel_size());
        let incoming_stream = request.into_inner();

        // Build the router object
        let router = Router::new(remote_address, false, self.hub_sender.clone(), incoming_stream, outgoing_route).await;

        // Notify the central Hub about the new peer
        self.hub_sender.send(HubEvent::NewPeer(router)).await.expect("hub receiver should never drop before senders");
''',
     '''        // SEDRA (security back-port, upstream 2a47b249): bound pending handshakes globally and per source IP before
        // allocating the router and its channels.
        let inbound_handshake_guard =
            PendingInboundHandshakeGuard::try_new(self.pending_inbound_handshakes.clone(), remote_address.ip().to_canonical())
                .ok_or_else(|| TonicStatus::resource_exhausted("too many pending inbound handshakes"))?;

        // Build the in/out pipes
        let (outgoing_route, outgoing_receiver) = mpsc_channel(Self::outgoing_network_channel_size());
        let incoming_stream = request.into_inner();

        // Build the router object
        let router = Router::new(remote_address, false, self.hub_sender.clone(), incoming_stream, outgoing_route).await;

        // SEDRA (security back-port, upstream 2a47b249): run the handshake in a task of its own instead of inside the hub
        // event loop, and notify the hub only once it succeeded
        let initializer = self.initializer.clone();
        let hub_sender = self.hub_sender.clone();
        tokio::spawn(async move {
            // Hold the reservation until initialization and any failure cleanup complete
            let _inbound_handshake_guard = inbound_handshake_guard;
            match initializer.initialize_connection(router.clone()).await {
                Ok(()) => {
                    hub_sender.send(HubEvent::NewPeer(router)).await.expect("hub receiver should never drop before senders");
                }
                Err(err) => {
                    router.try_sending_reject_message(&err).await;
                    router.close().await;
                    if matches!(err, ProtocolError::LoopbackConnection(_) | ProtocolError::PeerAlreadyExists(_)) {
                        debug!("P2P, handshake failed for inbound peer {}: {}", router, err);
                    } else {
                        warn!("P2P, handshake failed for inbound peer {}: {}", router, err);
                    }
                }
            }
        });
'''),
])
p = pathlib.Path(C)
p.write_text(p.read_text().rstrip("\n") + '''

#[cfg(test)]
mod sedra_backport_tests {
    use super::*;
    use std::net::{Ipv4Addr, Ipv6Addr};

    /// SEDRA (security back-port, upstream 2a47b249; test ported from upstream): pending inbound handshakes are limited per
    /// IP and in total, and slots are reused once released.
    #[test]
    fn pending_inbound_handshake_limits_and_reuses_slots_test() {
        let pending = Arc::new(Mutex::new(PendingInboundHandshakes::default()));
        let ip = IpAddr::V4(Ipv4Addr::LOCALHOST);

        let first = PendingInboundHandshakeGuard::try_new(pending.clone(), ip).unwrap();
        let second = PendingInboundHandshakeGuard::try_new(pending.clone(), ip).unwrap();
        assert!(PendingInboundHandshakeGuard::try_new(pending.clone(), ip).is_none(), "third handshake from one IP must be refused");

        drop(first);
        let replacement = PendingInboundHandshakeGuard::try_new(pending.clone(), ip).unwrap();
        drop((second, replacement));

        let mut guards = Vec::with_capacity(MAX_PENDING_INBOUND_HANDSHAKES);
        for i in 0..MAX_PENDING_INBOUND_HANDSHAKES {
            let ip = IpAddr::V6(Ipv6Addr::from(u128::try_from(i).unwrap()));
            guards.push(PendingInboundHandshakeGuard::try_new(pending.clone(), ip).unwrap());
        }
        let next_ip = IpAddr::V6(Ipv6Addr::from(u128::try_from(MAX_PENDING_INBOUND_HANDSHAKES).unwrap()));
        assert!(PendingInboundHandshakeGuard::try_new(pending.clone(), next_ip).is_none(), "global limit must be enforced");

        drop(guards);
        let pending = pending.lock();
        assert_eq!(pending.total, 0);
        assert!(pending.by_ip.is_empty());
    }
}
''')
print("inbound handshake hardening applied")

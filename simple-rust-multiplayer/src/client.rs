use tokio::net::UdpSocket;
use std::net::SocketAddr;

pub struct Client {
    socket: UdpSocket,
    peer: SocketAddr,
}

impl Client {
    pub async fn new(bind_port: u16, peer: SocketAddr) -> Self {
        let socket = UdpSocket::bind(("0.0.0.0", bind_port))
            .await
            .expect("bind failed");

        socket.connect(peer).await.expect("connect failed");

        Self { socket, peer }
    }

    pub async fn send(&self, data: &[u8]) {
        let _ = self.socket.send(data).await;
    }

    pub async fn receive(&self, buffer: &mut [u8]) -> usize {
        self.socket.recv(buffer).await.unwrap_or(0)
    }
}

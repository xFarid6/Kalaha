use tokio::net::UdpSocket;
use std::net::SocketAddr;

pub async fn run_meet_server(port: u16) {
    let socket = UdpSocket::bind(("0.0.0.0", port))
        .await
        .expect("failed to bind meet server");

    println!("Meet server listening on {}", port);

    let mut clients: Vec<SocketAddr> = Vec::new();
    let mut buf = [0u8; 128];

    loop {
        let (_, addr) = socket.recv_from(&mut buf).await.unwrap();

        if !clients.contains(&addr) {
            clients.push(addr);
            println!("Client registered: {}", addr);
        }

        if clients.len() == 2 {
            let a = clients[0];
            let b = clients[1];

            socket.send_to(b.to_string().as_bytes(), a).await.unwrap();
            socket.send_to(a.to_string().as_bytes(), b).await.unwrap();

            println!("Matched {} <-> {}", a, b);
            clients.clear();
        }
    }
}

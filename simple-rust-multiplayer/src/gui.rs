use bevy::prelude::*;
use crate::AppState;

#[derive(Resource)]
pub enum Mode {
    Server,
    Client,
}

#[derive(Component)]
pub struct MyPlayer;

#[derive(Component)]
pub struct RemotePlayer;

pub fn select_mode_ui(
    mut commands: Commands,
    mut state: ResMut<NextState<AppState>>,
    keyboard: Res<Input<KeyCode>>,
) {
    if keyboard.just_pressed(KeyCode::S) {
        commands.insert_resource(Mode::Server);
        state.set(AppState::NetworkSetup);
    }

    if keyboard.just_pressed(KeyCode::C) {
        commands.insert_resource(Mode::Client);
        state.set(AppState::NetworkSetup);
    }
}

pub fn network_setup_ui(
    mut state: ResMut<NextState<AppState>>,
    keyboard: Res<Input<KeyCode>>,
) {
    // Placeholder UI:
    // premi ENTER per continuare
    if keyboard.just_pressed(KeyCode::Return) {
        state.set(AppState::InGame);
    }
}

pub fn spawn_players(mut commands: Commands) {
    commands.spawn((
        SpriteBundle {
            sprite: Sprite {
                color: Color::GREEN,
                custom_size: Some(Vec2::new(50.0, 50.0)),
                ..default()
            },
            transform: Transform::from_xyz(-100.0, 0.0, 0.0),
            ..default()
        },
        MyPlayer,
    ));

    commands.spawn((
        SpriteBundle {
            sprite: Sprite {
                color: Color::RED,
                custom_size: Some(Vec2::new(50.0, 50.0)),
                ..default()
            },
            transform: Transform::from_xyz(100.0, 0.0, 0.0),
            ..default()
        },
        RemotePlayer,
    ));
}

pub fn game_tick(
    keyboard: Res<Input<KeyCode>>,
    mut query: Query<&mut Transform, With<MyPlayer>>,
) {
    let mut transform = query.single_mut();

    let speed = 5.0;

    if keyboard.pressed(KeyCode::Left) {
        transform.translation.x -= speed;
    }
    if keyboard.pressed(KeyCode::Right) {
        transform.translation.x += speed;
    }
    if keyboard.pressed(KeyCode::Up) {
        transform.translation.y += speed;
    }
    if keyboard.pressed(KeyCode::Down) {
        transform.translation.y -= speed;
    }
}

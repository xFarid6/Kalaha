mod gui;
mod client;
mod server;
mod constants;

use bevy::prelude::*;
use gui::*;

#[derive(States, Debug, Clone, Eq, PartialEq, Hash, Default)]
pub enum AppState {
    #[default]
    SelectMode,
    NetworkSetup,
    InGame,
}

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_state::<AppState>()
        .insert_resource(ClearColor(Color::rgb(0.1, 0.1, 0.1)))
        .add_systems(Startup, setup_camera)
        .add_systems(Update, (
            gui::select_mode_ui,
            gui::network_setup_ui,
        ))
        .add_systems(OnEnter(AppState::InGame), gui::spawn_players)
        .add_systems(
            FixedUpdate,
            gui::game_tick
        )
        .run();
}

fn setup_camera(mut commands: Commands) {
    commands.spawn(Camera2dBundle::default());
}

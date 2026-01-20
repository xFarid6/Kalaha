import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart'; // For kIsWeb
import 'package:http/http.dart' as http;
import '../models/note.dart';

class ApiService {
  // Helper to get the correct URL depending on the platform.
  // Android Emulator uses 10.0.2.2 to access the host machine's localhost.
  static String get baseUrl {
    if (kIsWeb) return 'http://localhost:8080'; // Web always standard
    if (Platform.isAndroid) return 'http://10.0.2.2:8080';
    return 'http://localhost:8080'; // Windows/Linux/macOS
  }

  Future<List<Note>> getNotes() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/notes'));

      if (response.statusCode == 200) {
        final List<dynamic> body = jsonDecode(response.body);
        return body.map((json) => Note.fromJson(json)).toList();
      } else {
        throw Exception('Server Error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to connect to server: $e');
    }
  }

  Future<Note> createNote(String title, String body) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/notes'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'title': title, 'body': body}),
      );

      if (response.statusCode == 201) {
        return Note.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to create note: ${response.body}');
      }
    } catch (e) {
      throw Exception('Connection error: $e');
    }
  }

  Future<void> deleteNote(String id) async {
    try {
      final response = await http.delete(Uri.parse('$baseUrl/notes?id=$id'));

      if (response.statusCode != 200) {
        throw Exception('Failed to delete note');
      }
    } catch (e) {
      throw Exception('Connection error: $e');
    }
  }
}

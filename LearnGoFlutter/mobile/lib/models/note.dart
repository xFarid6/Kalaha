class Note {
  final String id;
  final String title;
  final String body;

  Note({
    required this.id,
    required this.title,
    required this.body,
  });

  // Factory constructor to create a Note from JSON Key-Value pairs
  factory Note.fromJson(Map<String, dynamic> json) {
    return Note(
      id: json['id'] as String? ?? '', // Handle potential nulls safely
      title: json['title'] as String? ?? 'Untitled',
      body: json['body'] as String? ?? '',
    );
  }

  // Method to convert Note instance to JSON for sending to API
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'body': body,
    };
  }
}

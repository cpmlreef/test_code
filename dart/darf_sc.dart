import 'package:http/http.dart' as http;
void main() async {
  var res = await http.get(Uri.parse('https://example.com'));
  print('pub works: ${res.statusCode}');
}

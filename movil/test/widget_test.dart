import 'package:flutter_test/flutter_test.dart';
import 'package:movil/main.dart';

void main() {
  testWidgets('Pantalla de inicio de sesión', (tester) async {
    await tester.pumpWidget(const PeajeApp());

    expect(
      find.text('Iniciar sesión con Google'),
      findsOneWidget,
    );
  });
}
import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:camera/camera.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const baseUrl = 'https://peaje-inteligente-xkd1.onrender.com';

const googleClientId =
    '344925133510-7coh2a2t16juqjhoejnvv9kpht5gha1v.apps.googleusercontent.com';

const storage = FlutterSecureStorage();

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await GoogleSignIn.instance.initialize(
    serverClientId: googleClientId,
  );

  runApp(const PeajeApp());
}

class PeajeApp extends StatelessWidget {
  const PeajeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Peaje Inteligente',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF123B65),
        ),
      ),
      home: const LoginPage(),
    );
  }
}

class Api {
  static String token = '';

  static Map<String, String> get headers => {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      };

  static dynamic decode(http.Response response) {
    final data = jsonDecode(utf8.decode(response.bodyBytes));

    if (response.statusCode >= 400) {
      throw Exception(data.toString());
    }

    return data;
  }

  static Future<dynamic> get(String path) async {
    final response = await http
        .get(Uri.parse('$baseUrl$path'), headers: headers)
        .timeout(const Duration(seconds: 120));

    return decode(response);
  }

  static Future<dynamic> post(
    String path,
    Map<String, dynamic> data,
  ) async {
    final response = await http
        .post(
          Uri.parse('$baseUrl$path'),
          headers: headers,
          body: jsonEncode(data),
        )
        .timeout(const Duration(seconds: 120));

    return decode(response);
  }

  static Future<dynamic> upload(
    String path,
    XFile image, {
    Map<String, String> fields = const {},
  }) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl$path'),
    );

    request.headers['Authorization'] = 'Bearer $token';
    request.fields.addAll(fields);

    request.files.add(
      await http.MultipartFile.fromPath(
        'imagen',
        image.path,
      ),
    );

    final streamed = await request
        .send()
        .timeout(const Duration(seconds: 150));

    final response = await http.Response.fromStream(streamed);

    return decode(response);
  }
}

// =====================================================
// LOGIN CON GOOGLE
// =====================================================

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  bool loading = false;
  String error = '';

  Future<void> login() async {
    setState(() {
      loading = true;
      error = '';
    });

    try {
      final account =
          await GoogleSignIn.instance.authenticate();

      final authentication = account.authentication;
      final idToken = authentication.idToken;

      if (idToken == null) {
        throw Exception('Google no devolvió el token.');
      }

      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/auth/google'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'id_token': idToken,
        }),
      ).timeout(const Duration(seconds: 120));

      final data = Api.decode(response);

      Api.token = data['access'];

      await storage.write(
        key: 'access_token',
        value: Api.token,
      );

      await storage.write(
        key: 'refresh_token',
        value: data['refresh']?.toString() ?? '',
      );

      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => HomePage(
            usuario: Map<String, dynamic>.from(
              data['usuario'],
            ),
          ),
        ),
      );
    } catch (e) {
      if (mounted) {
        setState(() {
          error = e.toString();
        });
      }
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF123B65),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(30),
          child: Column(
            children: [
              const Icon(
                Icons.directions_car,
                size: 100,
                color: Colors.white,
              ),
              const SizedBox(height: 25),
              const Text(
                'PEAJE INTELIGENTE',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'Sistema inteligente de control vehicular',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white70),
              ),
              const SizedBox(height: 40),
              if (loading)
                const CircularProgressIndicator(
                  color: Colors.white,
                )
              else
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: login,
                    icon: const Icon(Icons.login),
                    label: const Text(
                      'Iniciar sesión con Google',
                    ),
                  ),
                ),
              if (error.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 20),
                  child: Text(
                    error,
                    style: const TextStyle(
                      color: Colors.orangeAccent,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

// =====================================================
// MENU PRINCIPAL
// =====================================================

class HomePage extends StatelessWidget {
  final Map<String, dynamic> usuario;

  const HomePage({
    super.key,
    required this.usuario,
  });

  Future<void> logout(BuildContext context) async {
    await GoogleSignIn.instance.signOut();
    await storage.deleteAll();

    Api.token = '';

    if (!context.mounted) return;

    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(
        builder: (_) => const LoginPage(),
      ),
      (_) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Peaje Inteligente'),
        actions: [
          IconButton(
            onPressed: () => logout(context),
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            'Bienvenido, ${usuario['nombre']}',
            style: const TextStyle(
              fontSize: 23,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text('Rol: ${usuario['rol']}'),
          const SizedBox(height: 25),
          Card(
            child: ListTile(
              contentPadding: const EdgeInsets.all(20),
              leading: const Icon(
                Icons.videocam,
                size: 45,
              ),
              title: const Text('Modo Caseta'),
              subtitle: const Text(
                'Capturar vehículos y registrar pasos',
              ),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const CasetaPage(),
                ),
              ),
            ),
          ),
          const SizedBox(height: 15),
          Card(
            child: ListTile(
              contentPadding: const EdgeInsets.all(20),
              leading: const Icon(
                Icons.chat,
                size: 45,
              ),
              title: const Text('Modo Consulta'),
              subtitle: const Text(
                'Consultar placas por texto o imagen',
              ),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const ConsultaPage(),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// =====================================================
// MODO CASETA
// =====================================================

class CasetaPage extends StatefulWidget {
  const CasetaPage({super.key});

  @override
  State<CasetaPage> createState() => _CasetaPageState();
}

class _CasetaPageState extends State<CasetaPage> {
  CameraController? camera;
  bool cameraReady = false;
  bool running = false;
  bool busy = false;

  List<dynamic> casetas = [];
  int? casetaId;

  Map<String, dynamic>? resultado;
  String estado = 'Preparando cámara...';

  @override
  void initState() {
    super.initState();
    preparar();
  }

  Future<void> preparar() async {
    try {
      final data = await Api.get('/api/v1/casetas/');

      casetas = data is List
          ? data
          : (data['results'] as List? ?? []);

      if (casetas.isNotEmpty) {
        casetaId = casetas.first['id'];
      }

      final cameras = await availableCameras();

      if (cameras.isEmpty) {
        throw Exception('No hay cámaras disponibles.');
      }

      final selected = cameras.firstWhere(
        (c) => c.lensDirection == CameraLensDirection.back,
        orElse: () => cameras.first,
      );

      camera = CameraController(
        selected,
        ResolutionPreset.medium,
        enableAudio: false,
      );

      await camera!.initialize();

      if (!mounted) return;

      setState(() {
        cameraReady = true;
        estado = 'Cámara preparada';
      });
    } catch (e) {
      if (mounted) {
        setState(() => estado = e.toString());
      }
    }
  }

  Future<void> procesar(XFile image) async {
    if (busy || casetaId == null || !mounted) return;

    setState(() {
      busy = true;
      estado = 'Procesando vehículo...';
    });

    try {
      final data = await Api.upload(
        '/api/v1/pasos/frame',
        image,
        fields: {
          'caseta_id': casetaId.toString(),
        },
      );

      if (!mounted) return;

      setState(() {
        resultado = Map<String, dynamic>.from(data);
        estado = 'Vehículo procesado';
      });
    } catch (e) {
      if (mounted) {
        setState(() => estado = e.toString());
      }
    } finally {
      if (mounted) {
        setState(() => busy = false);
      }
    }
  }

  Future<void> capturar() async {
    if (!cameraReady || busy) return;

    try {
      final image = await camera!.takePicture();
      await procesar(image);
    } catch (e) {
      if (mounted) {
        setState(() => estado = e.toString());
      }
    }
  }

  Future<void> iniciarCaptura() async {
    if (!cameraReady || running) return;

    setState(() => running = true);

    while (running && mounted) {
      await capturar();

      await Future.delayed(
        const Duration(milliseconds: 500),
      );
    }
  }

  void detenerCaptura() {
    setState(() => running = false);
  }

  Future<void> galeria() async {
    final image = await ImagePicker().pickImage(
      source: ImageSource.gallery,
      imageQuality: 85,
    );

    if (image != null) {
      await procesar(image);
    }
  }

  @override
  void dispose() {
    running = false;
    camera?.dispose();
    super.dispose();
  }

  Widget dato(String nombre, dynamic valor) {
    return ListTile(
      dense: true,
      title: Text(nombre),
      trailing: Text(
        valor?.toString() ?? 'No detectado',
        style: const TextStyle(
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final aprobado = resultado?['estado'] == 'aprobado';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Modo Caseta'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          DropdownButtonFormField<int>(
            initialValue: casetaId,
            decoration: const InputDecoration(
              labelText: 'Seleccionar caseta',
              border: OutlineInputBorder(),
            ),
            items: casetas.map((c) {
              return DropdownMenuItem<int>(
                value: c['id'],
                child: Text(c['nombre'].toString()),
              );
            }).toList(),
            onChanged: running || busy
                ? null
                : (value) {
                    setState(() => casetaId = value);
                  },
          ),
          const SizedBox(height: 15),
          if (cameraReady)
            ClipRRect(
              borderRadius: BorderRadius.circular(15),
              child: AspectRatio(
                aspectRatio: 3 / 4,
                child: CameraPreview(camera!),
              ),
            )
          else
            const SizedBox(
              height: 180,
              child: Center(
                child: Icon(Icons.videocam, size: 60),
              ),
            ),
          const SizedBox(height: 15),
          FilledButton.icon(
            onPressed: !cameraReady
                ? null
                : running
                    ? detenerCaptura
                    : busy
                        ? null
                        : iniciarCaptura,
            icon: Icon(
              running ? Icons.stop : Icons.play_arrow,
            ),
            label: Text(
              running
                  ? 'Detener captura'
                  : 'Iniciar captura continua',
            ),
          ),
          OutlinedButton.icon(
            onPressed: running || busy || !cameraReady
                ? null
                : capturar,
            icon: const Icon(Icons.camera_alt),
            label: const Text('Capturar fotografía'),
          ),
          OutlinedButton.icon(
            onPressed: running || busy ? null : galeria,
            icon: const Icon(Icons.photo_library),
            label: const Text('Seleccionar imagen'),
          ),
          if (busy) const LinearProgressIndicator(),
          const SizedBox(height: 10),
          Text(
            estado,
            textAlign: TextAlign.center,
          ),
          if (resultado != null)
            Card(
              color: aprobado
                  ? Colors.green.shade50
                  : Colors.orange.shade50,
              child: Column(
                children: [
                  const Padding(
                    padding: EdgeInsets.all(15),
                    child: Text(
                      'RESULTADO DE INFERENCIA',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  dato(
                    'Placa',
                    resultado!['placa_normalizada'],
                  ),
                  dato(
                    'Categoría',
                    resultado!['categoria_detectada'],
                  ),
                  dato(
                    'Ejes',
                    resultado!['ejes_detectados'],
                  ),
                  dato(
                    'Tarifa',
                    'Bs. ${resultado!['monto']}',
                  ),
                  dato(
                    'Estado',
                    resultado!['estado'],
                  ),
                  dato(
                    'Latencia',
                    '${resultado!['latencia_ms']} ms',
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

// =====================================================
// MODO CONSULTA
// =====================================================

class ConsultaPage extends StatefulWidget {
  const ConsultaPage({super.key});

  @override
  State<ConsultaPage> createState() => _ConsultaPageState();
}

class _ConsultaPageState extends State<ConsultaPage> {
  final controller = TextEditingController();

  final List<Map<String, String>> mensajes = [];

  XFile? imagen;
  bool loading = false;

  Future<void> seleccionar(ImageSource source) async {
    final selected = await ImagePicker().pickImage(
      source: source,
      imageQuality: 85,
    );

    if (selected != null && mounted) {
      setState(() => imagen = selected);
    }
  }

  Future<void> enviar() async {
    final texto = controller.text.trim();
    final foto = imagen;

    if (texto.isEmpty && foto == null) return;

    setState(() {
      loading = true;

      mensajes.add({
        'rol': 'usuario',
        'texto': foto != null
            ? 'Consulta por imagen: $texto'
            : texto,
      });

      controller.clear();
      imagen = null;
    });

    try {
      dynamic data;

      if (foto != null) {
        data = await Api.upload(
          '/api/v1/agente/chat',
          foto,
          fields: {
            'mensaje': texto,
          },
        );
      } else {
        data = await Api.post(
          '/api/v1/agente/chat',
          {
            'mensaje': texto,
          },
        );
      }

      final respuesta =
          data['respuesta'] ??
          data['mensaje'] ??
          const JsonEncoder.withIndent('  ').convert(data);

      if (!mounted) return;

      setState(() {
        mensajes.add({
          'rol': 'agente',
          'texto': respuesta.toString(),
        });
      });
    } catch (e) {
      if (mounted) {
        setState(() {
          mensajes.add({
            'rol': 'agente',
            'texto': 'Error: $e',
          });
        });
      }
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Agente de consultas'),
      ),
      body: Column(
        children: [
          Expanded(
            child: mensajes.isEmpty
                ? const Center(
                    child: Text(
                      'Escribe una placa o envía una fotografía.',
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(15),
                    itemCount: mensajes.length,
                    itemBuilder: (_, index) {
                      final mensaje = mensajes[index];

                      final usuario =
                          mensaje['rol'] == 'usuario';

                      return Align(
                        alignment: usuario
                            ? Alignment.centerRight
                            : Alignment.centerLeft,
                        child: Container(
                          constraints: const BoxConstraints(
                            maxWidth: 300,
                          ),
                          margin: const EdgeInsets.only(
                            bottom: 12,
                          ),
                          padding: const EdgeInsets.all(15),
                          decoration: BoxDecoration(
                            color: usuario
                                ? Colors.blue.shade100
                                : Colors.grey.shade200,
                            borderRadius:
                                BorderRadius.circular(15),
                          ),
                          child: Text(mensaje['texto']!),
                        ),
                      );
                    },
                  ),
          ),
          if (loading) const LinearProgressIndicator(),
          if (imagen != null)
            Row(
              children: [
                Image.file(
                  File(imagen!.path),
                  height: 90,
                  width: 120,
                  fit: BoxFit.cover,
                ),
                IconButton(
                  onPressed: () {
                    setState(() => imagen = null);
                  },
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(8),
              child: Row(
                children: [
                  IconButton(
                    onPressed: loading
                        ? null
                        : () => seleccionar(
                              ImageSource.camera,
                            ),
                    icon: const Icon(Icons.camera_alt),
                  ),
                  IconButton(
                    onPressed: loading
                        ? null
                        : () => seleccionar(
                              ImageSource.gallery,
                            ),
                    icon: const Icon(Icons.image),
                  ),
                  Expanded(
                    child: TextField(
                      controller: controller,
                      decoration: const InputDecoration(
                        hintText: 'Consultar placa...',
                        border: OutlineInputBorder(),
                      ),
                      onSubmitted: (_) {
                        if (!loading) enviar();
                      },
                    ),
                  ),
                  IconButton(
                    onPressed: loading ? null : enviar,
                    icon: const Icon(Icons.send),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
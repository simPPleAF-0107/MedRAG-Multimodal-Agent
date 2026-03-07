import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/api_service.dart';
import '../providers/report_provider.dart';
import '../widgets/upload_widget.dart';

// Note: To support actual image picking on real devices, we'd use image_picker.
// For this scaffolding/prototype, we'll simulate the multimodal attachment.

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  final _symptomController = TextEditingController();
  bool _isLoading = false;
  String _statusMessage = '';

  Future<void> _handleUpload() async {
    if (_symptomController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter clinical observations.')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _statusMessage = 'Analyzing Vectors...';
    });

    try {
      // Simulate real API execution
      final response = await ApiService().generateReport(_symptomController.text);
      
      if (mounted) {
        context.read<ReportProvider>().setLatestReport(response);
        
        setState(() {
          _statusMessage = 'Diagnosis Complete!';
        });

        // Normally we'd use a tab controller to switch tabs automatically
        ScaffoldMessenger.of(context).showSnackBar(
           const SnackBar(
             content: Text('Pipeline Complete. Open the Reports Tab to view results.'),
             backgroundColor: Colors.green,
             duration: Duration(seconds: 4),
           )
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Diagnostic Inference Engine')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Trigger Multimodal RAG Pipeline',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Provide clinical context and attach required visual evidence to initialize analysis.',
              style: TextStyle(color: Colors.grey.shade600),
            ),
            const SizedBox(height: 32),

            // Symptoms
            const Text('Clinical Observations', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            TextField(
              controller: _symptomController,
              maxLines: 5,
              decoration: InputDecoration(
                hintText: 'e.g. Patient presents with sharp abdominal pain...',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                filled: true,
                fillColor: Colors.white,
              ),
            ),
            const SizedBox(height: 24),

            // File Attachment Widgets
            const Text('Multimodal Evidence', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            UploadWidget(
              onTextFileTap: () {
                ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('File picker stub')));
              },
              onImageTap: () {
                ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Image picker stub')));
              },
            ),

            const SizedBox(height: 48),

            // Loading / Submit
            if (_isLoading)
              Column(
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 16),
                  Text(_statusMessage, style: const TextStyle(fontWeight: FontWeight.w600)),
                ],
              )
            else
              ElevatedButton.icon(
                onPressed: _handleUpload,
                icon: const Icon(Icons.psychology, color: Colors.white),
                label: const Text('Execute Pipeline', style: TextStyle(color: Colors.white, fontSize: 16)),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: Colors.blue.shade700,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              )
          ],
        ),
      ),
    );
  }
}

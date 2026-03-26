import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/api_service.dart';
import '../providers/report_provider.dart';
import '../widgets/upload_widget.dart';
import '../utils/ux_utils.dart';

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
  String? _attachedTextFile;
  String? _attachedImageFile;

  Future<void> _handleUpload() async {
    FocusScope.of(context).unfocus(); // Unfocus keyboard
    
    if (_symptomController.text.isEmpty) {
      UxUtils.showToast(context, 'Please enter clinical observations.', isError: true);
      return;
    }

    UxUtils.hapticMedium();

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

        UxUtils.hapticMedium();
        UxUtils.showToast(context, 'Pipeline Complete. Open the Reports Tab to view results.');
        _symptomController.clear();
      }
    } catch (e) {
      if (mounted) {
        UxUtils.showToast(context, 'Pipeline error: ${e.toString()}', isError: true);
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
        padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 32.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Trigger Multimodal RAG Pipeline',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              'Provide clinical context and attach required visual evidence to initialize analysis.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
            const SizedBox(height: 32),

            // Symptoms
            Text('Clinical Observations', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            TextField(
              controller: _symptomController,
              maxLines: 5,
              decoration: InputDecoration(
                hintText: 'e.g. Patient presents with sharp abdominal pain...',
              ),
            ),
            const SizedBox(height: 32),

            // File Attachment Widgets
            Text('Multimodal Evidence', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            UploadWidget(
              onTextFileTap: () {
                UxUtils.hapticLight();
                setState(() => _attachedTextFile = 'clinical_notes_log.txt');
                UxUtils.showToast(context, 'clinical_notes_log.txt attached');
              },
              onImageTap: () {
                UxUtils.hapticLight();
                setState(() => _attachedImageFile = 'radiology_scan.jpg');
                UxUtils.showToast(context, 'radiology_scan.jpg attached');
              },
            ),
            
            // Show attached files
            if (_attachedTextFile != null || _attachedImageFile != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Theme.of(context).primaryColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Theme.of(context).primaryColor.withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (_attachedTextFile != null) Row(
                      children: [
                        const Icon(Icons.description, size: 16, color: Colors.blue),
                        const SizedBox(width: 8),
                        Text(_attachedTextFile!, style: const TextStyle(fontWeight: FontWeight.bold)),
                      ]
                    ),
                    if (_attachedImageFile != null) Padding(
                      padding: const EdgeInsets.only(top: 8.0),
                      child: Row(
                        children: [
                          const Icon(Icons.image, size: 16, color: Colors.green),
                          const SizedBox(width: 8),
                          Text(_attachedImageFile!, style: const TextStyle(fontWeight: FontWeight.bold)),
                        ]
                      ),
                    ),
                  ],
                ),
              )
            ],

            const SizedBox(height: 48),

            // Loading / Submit
            if (_isLoading)
              Column(
                children: [
                  UxUtils.loadingSkeleton(height: 56, borderRadius: 12),
                  const SizedBox(height: 16),
                  Text(_statusMessage, style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: Theme.of(context).primaryColor,
                  )),
                ],
              )
            else
              ElevatedButton.icon(
                onPressed: _handleUpload,
                icon: const Icon(Icons.psychology_rounded, size: 24),
                label: const Text('Execute Pipeline'),
              )
          ],
        ),
      ),
    );
  }
}

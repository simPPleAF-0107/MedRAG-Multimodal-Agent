import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import 'package:image_picker/image_picker.dart';

import '../services/api_service.dart';
import '../providers/report_provider.dart';
import '../widgets/upload_widget.dart';
import '../utils/ux_utils.dart';
import '../utils/theme.dart';

class AttachedFile {
  final String name;
  final Uint8List bytes;
  final bool isImage;
  AttachedFile(this.name, this.bytes, this.isImage);
}

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  final _symptomController = TextEditingController();
  bool _isLoading = false;
  String _statusMessage = '';

  // Actual file data
  final List<AttachedFile> _attachedFiles = [];

  Future<void> _pickTextFile() async {
    UxUtils.hapticLight();
    try {
      final result = await FilePicker.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['txt', 'pdf', 'doc', 'docx', 'csv', 'json'],
        withData: true,
        allowMultiple: true,
      );

      if (result != null && result.files.isNotEmpty) {
        if (mounted) {
          setState(() {
            for (var file in result.files) {
              if (file.bytes != null) {
                _attachedFiles.add(AttachedFile(file.name, file.bytes!, false));
              }
            }
          });
          UxUtils.showToast(context, '${result.files.length} document(s) attached');
        }
      }
    } catch (e) {
      if (mounted) {
        UxUtils.showToast(context, 'Could not pick file: $e', isError: true);
      }
    }
  }

  Future<void> _pickImage() async {
    UxUtils.hapticLight();

    // Show bottom sheet to choose camera or gallery
    final source = await showModalBottomSheet<dynamic>(
      context: context,
      backgroundColor: MedRagTheme.surfaceDark,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Text(
                'Select Image Source',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 20),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: MedRagTheme.primaryCyan.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.camera_alt_rounded, color: MedRagTheme.primaryCyan),
                ),
                title: const Text('Camera', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                subtitle: Text('Take a new photo', style: TextStyle(color: MedRagTheme.textMuted)),
                onTap: () => Navigator.pop(ctx, ImageSource.camera),
              ),
              const SizedBox(height: 8),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF8B5CF6).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.photo_library_rounded, color: Color(0xFF8B5CF6)),
                ),
                title: const Text('Gallery', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                subtitle: Text('Choose multiple photos from gallery', style: TextStyle(color: MedRagTheme.textMuted)),
                onTap: () => Navigator.pop(ctx, "multi"), // Custom ID to denote multiple
              ),
            ],
          ),
        ),
      ),
    );

    if (source == null) return;

    try {
      final picker = ImagePicker();
      
      if (source is String && source == "multi") {
         final List<XFile> images = await picker.pickMultiImage(
           imageQuality: 85,
         );
         if (images.isNotEmpty) {
           for (var img in images) {
              final bytes = await img.readAsBytes();
              if (mounted) {
                setState(() {
                  _attachedFiles.add(AttachedFile(img.name, bytes, true));
                });
              }
           }
           if (mounted) {
             UxUtils.showToast(context, '${images.length} image(s) attached');
           }
         }
      } else if (source is ImageSource) {
        final XFile? image = await picker.pickImage(
          source: source,
          maxWidth: 1920,
          maxHeight: 1920,
          imageQuality: 85,
        );

        if (image != null) {
          final bytes = await image.readAsBytes();
          if (mounted) {
            setState(() {
              _attachedFiles.add(AttachedFile(image.name, bytes, true));
            });
            UxUtils.showToast(context, '${image.name} attached');
          }
        }
      }
    } catch (e) {
      if (mounted) {
        UxUtils.showToast(context, 'Could not pick image: $e', isError: true);
      }
    }
  }

  void _removeFile(int index) {
    UxUtils.hapticLight();
    setState(() {
      _attachedFiles.removeAt(index);
    });
  }

  Future<void> _handleUpload() async {
    FocusScope.of(context).unfocus();

    if (_symptomController.text.isEmpty && _attachedFiles.isEmpty) {
      UxUtils.showToast(context, 'Please provide context or attach files.', isError: true);
      return;
    }

    UxUtils.hapticMedium();

    setState(() {
      _isLoading = true;
      _statusMessage = 'Analyzing Vectors...';
    });

    try {
      final response = await ApiService().generateReport(
        _symptomController.text,
        files: _attachedFiles.map((f) => {
          'name': f.name,
          'bytes': f.bytes
        }).toList(),
      );

      if (mounted) {
        context.read<ReportProvider>().setLatestReport(response);

        setState(() {
          _statusMessage = 'Diagnosis Complete!';
        });

        UxUtils.hapticMedium();
        UxUtils.showToast(context, 'Pipeline Complete. Open the Reports Tab to view results.');
        _symptomController.clear();
        setState(() {
           _attachedFiles.clear();
        });
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
                    color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
                  ),
            ),
            const SizedBox(height: 32),

            // Symptoms
            Text('Clinical Observations', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            TextField(
              controller: _symptomController,
              maxLines: 5,
              decoration: const InputDecoration(
                hintText: 'e.g. Patient presents with sharp abdominal pain...',
              ),
            ),
            const SizedBox(height: 32),

            // File Attachment Widgets
            Text('Multimodal Evidence', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            UploadWidget(
              onTextFileTap: _pickTextFile,
              onImageTap: _pickImage,
            ),

            // Show attached files with remove buttons
            if (_attachedFiles.isNotEmpty) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: MedRagTheme.primaryCyan.withValues(alpha: 0.06),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: MedRagTheme.primaryCyan.withValues(alpha: 0.2)),
                ),
                child: ListView.separated(
                  physics: const NeverScrollableScrollPhysics(),
                  shrinkWrap: true,
                  itemCount: _attachedFiles.length,
                  separatorBuilder: (_, __) => Divider(color: Colors.white.withValues(alpha: 0.08), height: 20),
                  itemBuilder: (context, index) {
                    final f = _attachedFiles[index];
                    return _buildAttachedFileRow(
                      icon: f.isImage ? Icons.image_rounded : Icons.description_rounded,
                      color: f.isImage ? const Color(0xFF34D399) : MedRagTheme.primaryCyan,
                      fileName: f.name,
                      fileSize: _formatFileSize(f.bytes.length),
                      onRemove: () => _removeFile(index),
                    );
                  },
                )
              ),
            ],

            const SizedBox(height: 48),

            // Loading / Submit
            if (_isLoading)
              Column(
                children: [
                  UxUtils.loadingSkeleton(height: 56, borderRadius: 12),
                  const SizedBox(height: 16),
                  Text(_statusMessage,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
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
              ),
            const SizedBox(height: 100), // Bottom padding for floating nav bar
          ],
        ),
      ),
    );
  }

  Widget _buildAttachedFileRow({
    required IconData icon,
    required Color color,
    required String fileName,
    required String fileSize,
    required VoidCallback onRemove,
  }) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, size: 18, color: color),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                fileName,
                style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 13),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              Text(
                fileSize,
                style: TextStyle(color: MedRagTheme.textMuted, fontSize: 11),
              ),
            ],
          ),
        ),
        IconButton(
          icon: Icon(Icons.close_rounded, color: Colors.white.withValues(alpha: 0.5), size: 18),
          onPressed: onRemove,
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(),
        ),
      ],
    );
  }

  String _formatFileSize(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }
}

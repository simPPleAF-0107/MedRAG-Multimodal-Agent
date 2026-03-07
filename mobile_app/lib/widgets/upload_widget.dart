import 'package:flutter/material.dart';

class UploadWidget extends StatelessWidget {
  final VoidCallback onTextFileTap;
  final VoidCallback onImageTap;

  const UploadWidget({
    super.key, 
    required this.onTextFileTap, 
    required this.onImageTap
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: InkWell(
            onTap: onTextFileTap,
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 16),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Column(
                children: [
                  Icon(Icons.description, color: Colors.blue.shade600, size: 32),
                  const SizedBox(height: 8),
                  Text(
                    'Upload Log',
                    style: TextStyle(
                      color: Colors.blue.shade700,
                      fontWeight: FontWeight.w600,
                    ),
                  )
                ],
              ),
            ),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: InkWell(
            onTap: onImageTap,
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 16),
              decoration: BoxDecoration(
                color: Colors.purple.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.purple.shade200),
              ),
              child: Column(
                children: [
                  Icon(Icons.image, color: Colors.purple.shade600, size: 32),
                  const SizedBox(height: 8),
                  Text(
                    'Attach Scan',
                    style: TextStyle(
                      color: Colors.purple.shade700,
                      fontWeight: FontWeight.w600,
                    ),
                  )
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}

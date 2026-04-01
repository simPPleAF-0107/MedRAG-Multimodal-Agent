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
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: onTextFileTap,
              borderRadius: BorderRadius.circular(16),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 20),
                decoration: BoxDecoration(
                  color: Theme.of(context).primaryColor.withValues(alpha: 0.05),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Theme.of(context).primaryColor.withValues(alpha: 0.2), width: 1.5),
                ),
                child: Column(
                  children: [
                    Icon(Icons.description_rounded, color: Theme.of(context).primaryColor, size: 36),
                    const SizedBox(height: 12),
                    Text(
                      'Upload Log',
                      style: TextStyle(
                        color: Theme.of(context).primaryColor,
                        fontWeight: FontWeight.w600,
                        fontSize: 15,
                      ),
                    )
                  ],
                ),
              ),
            ),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: onImageTap,
              borderRadius: BorderRadius.circular(16),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 20),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.secondary.withValues(alpha: 0.05),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Theme.of(context).colorScheme.secondary.withValues(alpha: 0.2), width: 1.5),
                ),
                child: Column(
                  children: [
                    Icon(Icons.image_rounded, color: Theme.of(context).colorScheme.secondary, size: 36),
                    const SizedBox(height: 12),
                    Text(
                      'Attach Scan',
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.secondary,
                        fontWeight: FontWeight.w600,
                        fontSize: 15,
                      ),
                    )
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

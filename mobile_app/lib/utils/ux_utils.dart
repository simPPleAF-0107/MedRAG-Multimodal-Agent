import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class UxUtils {
  /// Provides subtle haptic feedback using light impact.
  /// Used for small interactions like tapping a tab or selecting an item.
  static void hapticLight() {
    HapticFeedback.lightImpact();
  }

  /// Provides medium haptic feedback using medium impact.
  /// Used for prominent buttons like "Submit" or form completions.
  static void hapticMedium() {
    HapticFeedback.mediumImpact();
  }

  /// Provides haptic feedback suitable for errors.
  static void hapticError() {
    HapticFeedback.heavyImpact();
  }

  /// Shows a customized modern sliding toast notification snackbar.
  static void showToast(BuildContext context, String message, {bool isError = false}) {
    if (isError) hapticError();
    
    // Dismiss existing
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    
    // Show new
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              isError ? Icons.error_outline : Icons.check_circle_outline,
              color: Colors.white,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message,
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w500),
              ),
            ),
          ],
        ),
        backgroundColor: isError ? Colors.red.shade600 : Colors.teal.shade700,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
        duration: const Duration(seconds: 3),
      ),
    );
  }

  /// Helper to generate a placeholder loading skeleton
  static Widget loadingSkeleton({double width = double.infinity, double height = 100, double borderRadius = 16}) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(borderRadius),
      ),
      // In a real app we'd use 'shimmer' package, but for prototype simple grey pulse is ok
      child: const Center(
        child: SizedBox(
          width: 24,
          height: 24,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(Colors.white24),
          ),
        ),
      ),
    );
  }

  /// Reusable empty state UI
  static Widget emptyState(String title, String subtitle, {IconData icon = Icons.inbox, VoidCallback? onAction, String? actionText}) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Icon(icon, size: 64, color: Colors.white.withValues(alpha: 0.3)),
            const SizedBox(height: 24),
            Text(
              title,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              subtitle,
              style: TextStyle(fontSize: 16, color: Colors.white.withValues(alpha: 0.5), height: 1.5),
              textAlign: TextAlign.center,
            ),
            if (onAction != null && actionText != null) ...[
              const SizedBox(height: 32),
              OutlinedButton(
                onPressed: () {
                  hapticLight();
                  onAction();
                },
                child: Text(actionText),
              )
            ]
          ],
        ),
      ),
    );
  }
}

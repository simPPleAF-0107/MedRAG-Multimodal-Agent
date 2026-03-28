import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../utils/theme.dart';

class ChatBubble extends StatelessWidget {
  final String text;
  final bool isUser;

  const ChatBubble({super.key, required this.text, required this.isUser});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 8),
        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 18),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
        decoration: BoxDecoration(
          color: isUser 
              ? MedRagTheme.primaryCyan.withOpacity(0.9) 
              : MedRagTheme.surfaceDark.withOpacity(0.5),
          border: isUser 
              ? Border.all(color: MedRagTheme.primaryCyan) 
              : Border.all(color: Colors.white.withOpacity(0.1)),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(24),
            topRight: const Radius.circular(24),
            bottomLeft: Radius.circular(isUser ? 24 : 6),
            bottomRight: Radius.circular(isUser ? 6 : 24),
          ),
          boxShadow: isUser 
              ? MedRagTheme.neonShadow 
              : [BoxShadow(color: Colors.black.withOpacity(0.2), blurRadius: 10)],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            if (!isUser) ...[
              Container(
                margin: const EdgeInsets.only(right: 10),
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: MedRagTheme.primaryCyan.withOpacity(0.2),
                  shape: BoxShape.circle,
                  border: Border.all(color: MedRagTheme.primaryCyan.withOpacity(0.5)),
                ),
                child: const Icon(Icons.psychology_outlined, color: MedRagTheme.primaryCyan, size: 16),
              ),
            ],
            Flexible(
              child: Text(
                text,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: isUser ? MedRagTheme.backgroundDark : MedRagTheme.textLight,
                  fontWeight: isUser ? FontWeight.w600 : FontWeight.w400,
                  height: 1.5,
                ),
              ),
            ),
            if (isUser) ...[
              Container(
                margin: const EdgeInsets.only(left: 10),
                child: const Icon(Icons.person, color: MedRagTheme.backgroundDark, size: 16),
              ),
            ],
          ],
        ),
      ).animate().fadeIn(duration: 400.ms).slideY(begin: 0.2, end: 0, curve: Curves.easeOutBack),
    );
  }
}

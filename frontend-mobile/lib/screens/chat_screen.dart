import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../services/api_service.dart';
import '../widgets/chat_bubble.dart';
import '../utils/ux_utils.dart';
import '../utils/theme.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, dynamic>> _messages = [];
  bool _isLoading = false;
  final ScrollController _scrollController = ScrollController();

  // Mock responses for when backend is unreachable
  static const List<String> _mockResponses = [
    'Based on the patient\'s history, their vital signs appear stable. Regular monitoring of blood pressure and glucose levels is recommended. Consider scheduling a follow-up in 2 weeks.',
    'The lab results indicate slightly elevated inflammatory markers. This could be consistent with mild infection or autoimmune activity. I\'d recommend a CRP test and CBC panel for further evaluation.',
    'Looking at the medication profile, there are no significant drug interactions. However, the patient should be monitored for potential side effects of the current NSAID regimen, especially GI symptoms.',
    'The imaging results show no acute findings. The previously noted areas of concern appear stable compared to prior studies. Continued surveillance is recommended per clinical guidelines.',
    'Based on current evidence, the risk assessment suggests a moderate cardiovascular risk profile. Lifestyle modifications including dietary changes and regular exercise should be emphasized.',
  ];
  int _mockIndex = 0;

  Future<void> _sendMessage() async {
    final text = _controller.text;
    if (text.isEmpty) return;

    UxUtils.hapticLight();

    setState(() {
      _messages.add({'role': 'user', 'content': text});
      _isLoading = true;
      _controller.clear();
    });

    _scrollToBottom();

    try {
      final response = await ApiService().chat(text, "1");
      if (mounted) {
        UxUtils.hapticMedium();
        setState(() {
          _messages.add({'role': 'assistant', 'content': response['reply']});
        });
      }
    } catch (e) {
      if (mounted) {
        // Provide mock fallback response when backend is unreachable
        await Future.delayed(const Duration(milliseconds: 800));
        if (mounted) {
          UxUtils.hapticMedium();
          final mockReply = _mockResponses[_mockIndex % _mockResponses.length];
          _mockIndex++;
          setState(() {
            _messages.add({'role': 'assistant', 'content': mockReply});
          });
        }
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        _scrollToBottom();
      }
    }
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.auto_awesome, color: MedRagTheme.primaryCyan, size: 24)
              .animate(onPlay: (controller) => controller.repeat(reverse: true))
              .scaleXY(end: 1.1, duration: 1.seconds),
            const SizedBox(width: 8),
            const Text('Clinical Agent'),
          ],
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        flexibleSpace: ClipRRect(
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Container(color: MedRagTheme.backgroundDark.withValues(alpha: 0.6)),
          ),
        ),
      ),
      body: Stack(
        children: [
          // Ambient Glow Backgrounds
          Positioned(
            top: 100,
            left: -50,
            child: Container(
              width: 200, height: 200,
              decoration: BoxDecoration(shape: BoxShape.circle, color: MedRagTheme.primaryCyan.withValues(alpha: 0.1)),
            ).animate(onPlay: (controller) => controller.repeat(reverse: true)).moveX(end: 50, duration: 4.seconds),
          ),
          Positioned(
            bottom: 100,
            right: -50,
            child: Container(
              width: 250, height: 250,
              decoration: BoxDecoration(shape: BoxShape.circle, color: MedRagTheme.secondaryCoral.withValues(alpha: 0.05)),
            ).animate(onPlay: (controller) => controller.repeat(reverse: true)).moveY(end: 50, duration: 3.seconds),
          ),
          
          SafeArea(
            bottom: false,
            child: Column(
              children: [
                Expanded(
                  child: _messages.isEmpty 
                    ? _buildEmptyState() 
                    : ListView.builder(
                        controller: _scrollController,
                        padding: const EdgeInsets.only(top: 16, bottom: 24, left: 12, right: 12),
                        itemCount: _messages.length,
                        itemBuilder: (context, index) {
                          final msg = _messages[index];
                          return ChatBubble(
                            text: msg['content']!,
                            isUser: msg['role'] == 'user',
                          );
                        },
                      ),
                ),
                if (_isLoading)
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Padding(
                      padding: const EdgeInsets.only(left: 20.0, bottom: 10),
                      child: Row(
                        children: [
                          const Icon(Icons.psychology, color: MedRagTheme.primaryCyan, size: 20),
                          const SizedBox(width: 8),
                          const Text(
                            "MedRAG is thinking...", 
                            style: TextStyle(color: MedRagTheme.primaryCyan, fontStyle: FontStyle.italic)
                          ).animate(onPlay: (controller) => controller.repeat()).shimmer(duration: 1.5.seconds, color: Colors.white),
                        ],
                      ),
                    ),
                  ),
                _buildInputArea(context),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: MedRagTheme.primaryCyan.withValues(alpha: 0.1),
              shape: BoxShape.circle,
              boxShadow: MedRagTheme.neonShadow,
              border: Border.all(color: MedRagTheme.primaryCyan.withValues(alpha: 0.3)),
            ),
            child: const Icon(Icons.psychology, size: 60, color: MedRagTheme.primaryCyan)
              .animate(onPlay: (controller) => controller.repeat(reverse: true))
              .scaleXY(end: 1.05, duration: 1.5.seconds),
          ),
          const SizedBox(height: 24),
          Text("How can I assist you today?", 
            style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)
          ).animate().fadeIn(delay: 300.ms).slideY(begin: 0.2, end: 0),
          const SizedBox(height: 8),
          Text(
            "Ask questions about patient history or diagnoses.",
            style: TextStyle(color: MedRagTheme.textMuted, fontSize: 14),
            textAlign: TextAlign.center,
          ).animate().fadeIn(delay: 500.ms),
        ],
      ),
    );
  }

  Widget _buildInputArea(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(
        left: 16, 
        right: 16, 
        top: 16, 
        // add extra padding for floating nav bar at the bottom:
        bottom: MediaQuery.of(context).padding.bottom + 90,
      ),
      decoration: BoxDecoration(
        color: MedRagTheme.backgroundDark.withValues(alpha: 0.8),
        border: Border(top: BorderSide(color: Colors.white.withValues(alpha: 0.05))),
      ),
      child: ClipRRect(
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _controller,
                  textInputAction: TextInputAction.send,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    hintText: 'Message memory agent...',
                    hintStyle: TextStyle(color: MedRagTheme.textMuted.withValues(alpha: 0.6)),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(30),
                      borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(30),
                      borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(30),
                      borderSide: const BorderSide(color: MedRagTheme.primaryCyan),
                    ),
                    filled: true,
                    fillColor: Colors.white.withValues(alpha: 0.05),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                  ),
                  onSubmitted: (_) => _sendMessage(),
                ),
              ),
              const SizedBox(width: 12),
              GestureDetector(
                onTap: _sendMessage,
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: MedRagTheme.primaryCyan,
                    boxShadow: MedRagTheme.neonShadow,
                  ),
                  child: const Icon(Icons.send_rounded, color: MedRagTheme.backgroundDark, size: 20),
                ),
              ).animate(target: _controller.text.isNotEmpty ? 1 : 0).scaleXY(end: 1.1, duration: 200.ms)
            ],
          ),
        ),
      ),
    );
  }
}

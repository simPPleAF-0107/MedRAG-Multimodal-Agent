import 'package:flutter/material.dart';
import '../../utils/ux_utils.dart';

class ActivityFormScreen extends StatefulWidget {
  const ActivityFormScreen({super.key});

  @override
  State<ActivityFormScreen> createState() => _ActivityFormScreenState();
}

class _ActivityFormScreenState extends State<ActivityFormScreen> {
  String _selectedActivity = 'Walking';
  String _intensityLevel = 'Moderate';
  final _durationController = TextEditingController();
  final _heartRateController = TextEditingController();

  void _submit() {
    FocusScope.of(context).unfocus();
    if (_durationController.text.isEmpty) {
      UxUtils.showToast(context, 'Please enter duration', isError: true);
      return;
    }
    UxUtils.hapticMedium();
    UxUtils.showToast(context, 'Activity logged successfully!');
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Activity Therapy')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Log Rehabilitation & Exercise', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 32),
            DropdownButtonFormField<String>(
              value: _selectedActivity,
              decoration: const InputDecoration(labelText: 'Activity Type'),
              items: ['Walking', 'Running', 'Cycling', 'Swimming', 'Physical Therapy'].map((String value) {
                return DropdownMenuItem<String>(value: value, child: Text(value));
              }).toList(),
              onChanged: (newValue) => setState(() => _selectedActivity = newValue!),
            ),
            const SizedBox(height: 24),
            DropdownButtonFormField<String>(
              value: _intensityLevel,
              decoration: const InputDecoration(labelText: 'Intensity Level'),
              items: ['Low', 'Moderate', 'High', 'Maximum Effort'].map((String value) {
                return DropdownMenuItem<String>(value: value, child: Text(value));
              }).toList(),
              onChanged: (newValue) => setState(() => _intensityLevel = newValue!),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _durationController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Duration (Min)',
                      prefixIcon: Icon(Icons.timer_outlined),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    controller: _heartRateController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Avg Heart Rate',
                      prefixIcon: Icon(Icons.favorite_border),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 48),
            SizedBox(
              height: 56,
              child: ElevatedButton(
                onPressed: _submit,
                child: const Text('Log Activity'),
              ),
            )
          ],
        ),
      ),
    );
  }
}

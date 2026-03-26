import 'package:flutter/material.dart';
import '../../utils/ux_utils.dart';

class MoodFormScreen extends StatefulWidget {
  const MoodFormScreen({super.key});

  @override
  State<MoodFormScreen> createState() => _MoodFormScreenState();
}

class _MoodFormScreenState extends State<MoodFormScreen> {
  double _moodValue = 5.0;
  double _stressValue = 5.0;
  double _sleepHours = 7.0;
  String _energyLevel = 'Medium';
  final TextEditingController _notesController = TextEditingController();

  void _submit() {
    UxUtils.hapticMedium();
    UxUtils.showToast(context, 'Mood logged successfully!');
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Psychiatric Mood Correlator')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('How are you feeling today?', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 32),
            Text('Overall Mood: ${_moodValue.toInt()}/10', style: Theme.of(context).textTheme.titleSmall),
            Slider(
              value: _moodValue,
              min: 1, max: 10, divisions: 9,
              activeColor: Theme.of(context).primaryColor,
              onChanged: (val) {
                UxUtils.hapticLight();
                setState(() => _moodValue = val);
              },
            ),
            const Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Depressed/Low'),
                Text('Euphoric/High'),
              ],
            ),
            const SizedBox(height: 32),
            Text('Stress Level: ${_stressValue.toInt()}/10', style: Theme.of(context).textTheme.titleSmall),
            Slider(
              value: _stressValue,
              min: 1, max: 10, divisions: 9,
              activeColor: Colors.deepOrangeAccent,
              onChanged: (val) {
                UxUtils.hapticLight();
                setState(() => _stressValue = val);
              },
            ),
            const SizedBox(height: 32),
            Text('Sleep Duration: ${_sleepHours.toStringAsFixed(1)} hours', style: Theme.of(context).textTheme.titleSmall),
            Slider(
              value: _sleepHours,
              min: 0, max: 16, divisions: 32,
              activeColor: Colors.indigoAccent,
              onChanged: (val) {
                UxUtils.hapticLight();
                setState(() => _sleepHours = val);
              },
            ),
            const SizedBox(height: 32),
            DropdownButtonFormField<String>(
              value: _energyLevel,
              decoration: const InputDecoration(labelText: 'Energy Level'),
              items: ['Low', 'Medium', 'High', 'Hyperactive'].map((String value) {
                return DropdownMenuItem<String>(value: value, child: Text(value));
              }).toList(),
              onChanged: (newValue) => setState(() => _energyLevel = newValue!),
            ),
            const SizedBox(height: 32),
            TextField(
              controller: _notesController,
              maxLines: 4,
              decoration: const InputDecoration(
                labelText: 'Clinical Notes / Triggers',
                alignLabelWithHint: true,
              ),
            ),
            const SizedBox(height: 48),
            SizedBox(
              height: 56,
              child: ElevatedButton(
                onPressed: _submit,
                child: const Text('Log Mood Correlation'),
              ),
            )
          ],
        ),
      ),
    );
  }
}

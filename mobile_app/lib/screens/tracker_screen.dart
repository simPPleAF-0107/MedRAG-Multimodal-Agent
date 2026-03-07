import 'package:flutter/material.dart';

// Unified Tracker View pointing conceptually to Mood, Activity, and Cycle forms.
class TrackerScreen extends StatelessWidget {
  const TrackerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Health Telemetry & Trackers')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildTrackerCard(
            context,
            Icons.mood,
            Colors.amber,
            'Psychiatric Mood Correlator',
            'Log daily subjective wellbeing.'
          ),
          const SizedBox(height: 16),
          _buildTrackerCard(
            context,
            Icons.directions_run,
            Colors.blue,
            'Activity Therapy Routing',
            'Log rehabilitation and exercise.'
          ),
          const SizedBox(height: 16),
          _buildTrackerCard(
            context,
            Icons.calendar_month,
            Colors.pink,
            'Reproductive Timeline',
            'Log physiological cycles.'
          ),
          const SizedBox(height: 16),
          _buildTrackerCard(
            context,
            Icons.restaurant,
            Colors.green,
            'Meal Planner',
            'Track dietary considerations.'
          ),
        ],
      ),
    );
  }

  Widget _buildTrackerCard(BuildContext context, IconData icon, Color color, String title, String subtitle) {
    return InkWell(
      onTap: () {
        ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Opening $title Form...'))
        );
      },
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.grey.shade200),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.02),
              blurRadius: 4,
              offset: const Offset(0, 2),
            )
          ]
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text(subtitle, style: TextStyle(fontSize: 14, color: Colors.grey.shade600)),
                ],
              ),
            ),
            Icon(Icons.chevron_right, color: Colors.grey.shade400)
          ],
        ),
      ),
    );
  }
}

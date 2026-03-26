import 'package:flutter/material.dart';
import '../utils/ux_utils.dart';
import 'forms/mood_form_screen.dart';
import 'forms/activity_form_screen.dart';
import 'forms/cycle_form_screen.dart';
import 'forms/meal_form_screen.dart';

// Unified Tracker View pointing conceptually to Mood, Activity, and Cycle forms.
class TrackerScreen extends StatelessWidget {
  const TrackerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Health Telemetry & Trackers')),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
        children: [
          _buildTrackerCard(
            context,
            Icons.mood,
            Colors.amber,
            'Psychiatric Mood Correlator',
            'Log daily subjective wellbeing.',
            const MoodFormScreen(),
          ),
          const SizedBox(height: 16),
          _buildTrackerCard(
            context,
            Icons.directions_run,
            Colors.blue,
            'Activity Therapy Routing',
            'Log rehabilitation and exercise.',
            const ActivityFormScreen(),
          ),
          const SizedBox(height: 16),
          _buildTrackerCard(
            context,
            Icons.calendar_month,
            Colors.pink,
            'Reproductive Timeline',
            'Log physiological cycles.',
            const CycleFormScreen(),
          ),
          const SizedBox(height: 16),
          _buildTrackerCard(
            context,
            Icons.restaurant,
            Colors.green,
            'Meal Planner',
            'Track dietary considerations.',
            const MealFormScreen(),
          ),
        ],
      ),
    );
  }

  Widget _buildTrackerCard(BuildContext context, IconData icon, Color color, String title, String subtitle, Widget targetScreen) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () {
            UxUtils.hapticLight();
            Navigator.of(context).push(MaterialPageRoute(builder: (_) => targetScreen));
          },
          borderRadius: BorderRadius.circular(16),
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Theme.of(context).cardTheme.color,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.grey.shade200),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.04),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                )
              ]
            ),
            child: Row(
              children: [
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 4),
                  Text(subtitle, style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6)
                  )),
                ],
              ),
            ),
            Icon(Icons.chevron_right_rounded, color: Colors.grey.shade400)
          ],
        ),
      ),
    ),
      ),
    );
  }
}

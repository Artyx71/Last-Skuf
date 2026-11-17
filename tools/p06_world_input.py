"""Strict actual Engine Input/velocity gate for the bounded WORLD preview.

Independently derive the fixed test route, never infer intended input from the
observed animation, displacement or self-reported expected fields. Focus state is
diagnostic only. This does not validate physical keyboard input or artistic feel.
"""
import math


DIRECTIONS = {'down': (0, 1), 'left': (-1, 0), 'right': (1, 0), 'up': (0, -1)}


def expected_samples():
    for direction in DIRECTIONS:
        for state, count in [('idle', 48), ('walk', 36), ('run', 36)]:
            vector = (0, 0) if state == 'idle' else DIRECTIONS[direction]
            yield from [('grid', state + '_' + direction, vector, state == 'run')] * count
    for state, direction in [('idle', 'up'), ('walk', 'right'), ('run', 'right'),
                             ('idle', 'right'), ('walk', 'down'), ('run', 'left'),
                             ('walk', 'up'), ('idle', 'up')]:
        vector = (0, 0) if state == 'idle' else DIRECTIONS[direction]
        yield from [('continuous', state + '_' + direction, vector, state == 'run')] * 24


def _number(value):
    if type(value) not in (float, int):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _vector_matches(value, expected, tolerance):
    return (isinstance(value, list) and len(value) == 2
            and all(_number(x) for x in value)
            and all(abs(a - b) <= tolerance for a, b in zip(value, expected)))


def validate_world_input(result, actor_id, speed):
    """Return a fail-closed, bounded diagnostic; do not mutate captured evidence."""
    errors = []
    violations = 0

    def reject(reason, sample=None):
        nonlocal violations
        violations += 1
        if len(errors) < 40:
            errors.append({'reason': reason, **({'sample': sample} if sample is not None else {})})

    report = {'schema': 1, 'scope': 'WORLD_PREVIEW_ENGINE_INPUT_SIGNAL_ONLY',
              'actor_id': actor_id, 'phase_approval': False, 'manual_keyboard_approval': False,
              'focus_efficacy_approval': False, 'expected_samples': 672,
              'matched_samples': 0, 'trace_samples': 0, 'errors': errors}
    if not isinstance(result, dict) or not _number(speed) or speed <= 0:
        reject('Invalid result or configured actor speed')
    else:
        if result.get('actor_id') != actor_id or result.get('actual_input') is not True:
            reject('Actor identity or actual_input evidence missing')
        if result.get('scope') != 'WORLD_ART_MOVEMENT_PREVIEW_ONLY':
            reject('Unexpected replay scope')
        if result.get('continuous_trace_start') != 480:
            reject('Continuous route boundary must be sample480')
        trace = result.get('trace')
        if not isinstance(trace, list):
            reject('Missing actual trace')
        else:
            report['trace_samples'] = len(trace)
            if len(trace) != 672:
                reject('Expected exactly672 route samples')
            previous_tick = -1
            for index, (point, plan) in enumerate(zip(trace, expected_samples())):
                before = violations
                sequence, animation, vector, running = plan
                if not isinstance(point, dict):
                    reject('Invalid sample object', index)
                    continue
                velocity = [axis * speed * (1.44 if running else 1.0) for axis in vector]
                if point.get('sequence') != sequence or point.get('animation') != animation:
                    reject('Observed route sequence/animation differs from independent plan', index)
                if not _vector_matches(point.get('input_vector'), vector, 0.000001):
                    reject('Actual Engine Input vector differs from plan', index)
                if point.get('run_pressed') is not running:
                    reject('Actual Shift state differs from plan', index)
                if not _vector_matches(point.get('velocity'), velocity, 0.001):
                    reject('Actual body velocity differs from configured speed/input', index)
                phase = point.get('frame')
                frame_count = 4 if animation.startswith('walk_') else 2
                if type(phase) is not int or not 0 <= phase < frame_count:
                    reject('Invalid animation frame index', index)
                tick = point.get('physics_tick')
                if type(tick) is not int or tick < previous_tick or tick < 0:
                    reject('Missing or reversed physics tick', index)
                else:
                    previous_tick = tick
                if before == violations:
                    report['matched_samples'] += 1
    report['violations'] = violations
    report['passed'] = violations == 0
    return report

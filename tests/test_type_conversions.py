"""Tests for type conversions and validation across the API."""

import pytest
from datetime import date
from app.models import WorkoutLogCreate, MacroEntryCreate, WorkoutLogUpdate, MacroEntryUpdate


class TestWorkoutLogTypeConversions:
    """Test type conversions for WorkoutLogCreate and WorkoutLogUpdate."""
    
    def test_create_with_date_object(self):
        """Test creating with Python date object."""
        workout = WorkoutLogCreate(
            exercise_id="ex1",
            log_date=date(2026, 3, 25),
            sets=4,
            reps=8,
            weight_kg=100.0,
        )
        assert isinstance(workout.log_date, date)
        assert workout.log_date == date(2026, 3, 25)
    
    def test_create_with_iso_date_string(self):
        """Test creating with ISO format date string."""
        workout = WorkoutLogCreate(
            exercise_id="ex1",
            log_date="2026-03-25",
            sets=4,
            reps=8,
            weight_kg=100.0,
        )
        assert isinstance(workout.log_date, date)
        assert workout.log_date == date(2026, 3, 25)
    
    def test_create_with_invalid_date_string(self):
        """Test that invalid date strings are rejected."""
        with pytest.raises(ValueError):
            WorkoutLogCreate(
                exercise_id="ex1",
                log_date="invalid-date",
                sets=4,
                reps=8,
                weight_kg=100.0,
            )
    
    def test_numeric_boundary_values_valid(self):
        """Test valid numeric boundary values."""
        # Minimum valid values
        workout1 = WorkoutLogCreate(
            exercise_id="ex1",
            log_date="2026-03-25",
            sets=1,
            reps=1,
            weight_kg=0.0,
        )
        assert workout1.sets == 1
        assert workout1.reps == 1
        assert workout1.weight_kg == 0.0
        
        # Maximum valid values
        workout2 = WorkoutLogCreate(
            exercise_id="ex1",
            log_date="2026-03-25",
            sets=100,
            reps=1000,
            weight_kg=1000.0,
        )
        assert workout2.sets == 100
        assert workout2.reps == 1000
        assert workout2.weight_kg == 1000.0
    
    def test_numeric_boundary_values_invalid(self):
        """Test that out-of-range numeric values are rejected."""
        # Sets too high
        with pytest.raises(ValueError):
            WorkoutLogCreate(
                exercise_id="ex1",
                log_date="2026-03-25",
                sets=101,  # Max is 100
                reps=8,
                weight_kg=100.0,
            )
        
        # Reps too high
        with pytest.raises(ValueError):
            WorkoutLogCreate(
                exercise_id="ex1",
                log_date="2026-03-25",
                sets=4,
                reps=1001,  # Max is 1000
                weight_kg=100.0,
            )
        
        # Weight too high
        with pytest.raises(ValueError):
            WorkoutLogCreate(
                exercise_id="ex1",
                log_date="2026-03-25",
                sets=4,
                reps=8,
                weight_kg=1001.0,  # Max is 1000
            )
        
        # Negative weight
        with pytest.raises(ValueError):
            WorkoutLogCreate(
                exercise_id="ex1",
                log_date="2026-03-25",
                sets=4,
                reps=8,
                weight_kg=-1.0,  # Min is 0
            )
    
    def test_update_with_partial_fields(self):
        """Test updating with only some fields."""
        update = WorkoutLogUpdate(
            log_date="2026-03-26",
            sets=5,
            # other fields omitted
        )
        assert isinstance(update.log_date, date)
        assert update.log_date == date(2026, 3, 26)
        assert update.sets == 5
        assert update.reps is None
        assert update.weight_kg is None
    
    def test_update_with_none_date(self):
        """Test updating with None date (should be allowed)."""
        update = WorkoutLogUpdate(
            log_date=None,
            sets=5,
        )
        assert update.log_date is None
        assert update.sets == 5


class TestMacroEntryTypeConversions:
    """Test type conversions for MacroEntryCreate and MacroEntryUpdate."""
    
    def test_create_with_date_object(self):
        """Test creating with Python date object."""
        macro = MacroEntryCreate(
            entry_date=date(2026, 3, 25),
            calories=2400.0,
            protein_g=180.0,
            carbs_g=260.0,
            fat_g=75.0,
        )
        assert isinstance(macro.entry_date, date)
        assert macro.entry_date == date(2026, 3, 25)
    
    def test_create_with_iso_date_string(self):
        """Test creating with ISO format date string."""
        macro = MacroEntryCreate(
            entry_date="2026-03-25",
            calories=2400.0,
            protein_g=180.0,
            carbs_g=260.0,
            fat_g=75.0,
        )
        assert isinstance(macro.entry_date, date)
        assert macro.entry_date == date(2026, 3, 25)
    
    def test_numeric_precision_preserved(self):
        """Test that float values preserve precision."""
        macro = MacroEntryCreate(
            entry_date="2026-03-25",
            calories=2350.5,
            protein_g=180.5,
            carbs_g=260.75,
            fat_g=75.25,
        )
        assert macro.calories == 2350.5
        assert macro.protein_g == 180.5
        assert macro.carbs_g == 260.75
        assert macro.fat_g == 75.25
    
    def test_numeric_boundary_values_valid(self):
        """Test valid numeric boundary values."""
        # Minimum values
        macro1 = MacroEntryCreate(
            entry_date="2026-03-25",
            calories=0.0,
            protein_g=0.0,
            carbs_g=0.0,
            fat_g=0.0,
        )
        assert macro1.calories == 0.0
        
        # Maximum values
        macro2 = MacroEntryCreate(
            entry_date="2026-03-25",
            calories=20000.0,
            protein_g=1000.0,
            carbs_g=2000.0,
            fat_g=1000.0,
        )
        assert macro2.calories == 20000.0


class TestDateEdgeCases:
    """Test date handling for edge cases."""
    
    def test_leap_year_date(self):
        """Test leap year date handling."""
        # 2024 is a leap year
        workout = WorkoutLogCreate(
            exercise_id="ex1",
            log_date="2024-02-29",
            sets=4,
            reps=8,
            weight_kg=100.0,
        )
        assert workout.log_date == date(2024, 2, 29)
    
    def test_year_boundary_date(self):
        """Test year boundary dates."""
        # End of year
        workout1 = WorkoutLogCreate(
            exercise_id="ex1",
            log_date="2026-12-31",
            sets=4,
            reps=8,
            weight_kg=100.0,
        )
        assert workout1.log_date == date(2026, 12, 31)
        
        # Start of year
        workout2 = WorkoutLogCreate(
            exercise_id="ex1",
            log_date="2026-01-01",
            sets=4,
            reps=8,
            weight_kg=100.0,
        )
        assert workout2.log_date == date(2026, 1, 1)
    
    def test_month_boundary_dates(self):
        """Test month boundary dates."""
        dates = [
            "2026-01-31",  # Jan 31
            "2026-04-30",  # Apr 30 (April has 30 days)
            "2026-02-28",  # Feb 28 (2026 is not a leap year)
        ]
        for date_str in dates:
            workout = WorkoutLogCreate(
                exercise_id="ex1",
                log_date=date_str,
                sets=4,
                reps=8,
                weight_kg=100.0,
            )
            assert isinstance(workout.log_date, date)

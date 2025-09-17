"""
Template filters for the application.

This module contains custom template filters for use in Jinja2 templates.
"""
from datetime import datetime
import math


def format_datetime(value, format='medium'):
    """Format a datetime object to a string.
    
    Args:
        value: The datetime object to format
        format: The format to use ('short', 'medium', 'long', 'full' or a custom format string)
    
    Returns:
        str: The formatted datetime string
    """
    if value is None:
        return ''
    
    if format == 'short':
        format = '%Y-%m-%d'
    elif format == 'medium':
        format = '%Y-%m-%d %H:%M'
    elif format == 'long':
        format = '%B %d, %Y %H:%M'
    elif format == 'full':
        format = '%A, %B %d, %Y at %I:%M %p'
    
    return value.strftime(format)


def format_date(value, format='medium'):
    """Format a date object to a string.
    
    Args:
        value: The date or datetime object to format
        format: The format to use ('short', 'medium', 'long', 'full' or a custom format string)
    
    Returns:
        str: The formatted date string
    """
    if value is None:
        return ''
    
    if format == 'short':
        format = '%m/%d/%y'
    elif format == 'medium':
        format = '%b %d, %Y'
    elif format == 'long':
        format = '%B %d, %Y'
    elif format == 'full':
        format = '%A, %B %d, %Y'
    
    return value.strftime(format)


def format_currency(value, currency='USD'):
    """Format a number as a currency string.
    
    Args:
        value: The number to format
        currency: The currency code (e.g., 'USD', 'EUR', 'GBP')
    
    Returns:
        str: The formatted currency string
    """
    if value is None:
        return ''
    
    # Simple currency formatting - can be extended with more currencies
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
    }
    
    symbol = currency_symbols.get(currency, currency)
    
    # Format the number with commas as thousand separators and 2 decimal places
    formatted_value = f"{float(value):,.2f}"
    
    return f"{symbol}{formatted_value}"


def format_duration(seconds):
    """Format a duration in seconds to a human-readable string.
    
    Args:
        seconds: The duration in seconds
    
    Returns:
        str: The formatted duration string
    """
    if not seconds and seconds != 0:
        return ''
    
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    parts = []
    
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return ' '.join(parts[:3])  # Return at most 3 parts


def pluralize(count, singular, plural=None):
    """Return the singular or plural form of a word based on the count.
    
    Args:
        count: The count to check
        singular: The singular form of the word
        plural: The plural form of the word (if None, adds 's' to singular)
    
    Returns:
        str: The appropriate form of the word
    """
    if count == 1:
        return singular
    
    if plural is not None:
        return plural
    
    return f"{singular}s"


def init_filters(app):
    """Register template filters with the Flask application."""
    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['date'] = format_date
    app.jinja_env.filters['currency'] = format_currency
    app.jinja_env.filters['duration'] = format_duration
    app.jinja_env.filters['pluralize'] = pluralize

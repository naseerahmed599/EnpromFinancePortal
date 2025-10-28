# Theme Styles Documentation

This directory contains all the glassmorphic, theme-adaptive CSS styling for the Flowwer Streamlit application.

## Structure

```
styles/
├── __init__.py          # Package initialization
├── theme_styles.py      # All CSS style functions
└── README.md           # This file
```

## Features

- **Theme-Adaptive**: Automatically adjusts to light/dark mode based on system preferences
- **Glassmorphic Design**: Modern frosted glass effect with backdrop blur
- **Modular**: Each component type has its own function
- **Reusable**: Easy to apply across different pages

## Usage

### Import the styles in your Streamlit app:

```python
from styles import get_all_document_page_styles, get_card_styles

# Apply all styles for All Documents page
st.markdown(get_all_document_page_styles(), unsafe_allow_html=True)

# Or use individual components
st.markdown(get_card_styles(), unsafe_allow_html=True)
```

### Available Style Functions:

1. **`get_page_header_styles()`**
   - Blue glassmorphic header cards
   - Use class: `page-header-card`

2. **`get_action_bar_styles()`**
   - Glassmorphic containers for primary buttons
   - Auto-applies to buttons with `kind="primary"`

3. **`get_export_bar_styles()`**
   - Glassmorphic containers for download/export buttons
   - Auto-applies to buttons with `kind="secondary"`

4. **`get_card_styles()`**
   - Metric cards, financial cards, payment cards
   - Section headers
   - Use classes: `metric-card-light`, `financial-card`, `section-header`

5. **`get_alert_box_styles()`**
   - Warning and info boxes
   - Use classes: `alert-box-orange`, `alert-box-purple`

6. **`get_all_document_page_styles()`**
   - Convenience function combining all styles
   - Perfect for the All Documents page

## CSS Classes Reference

### Cards
- `.page-header-card` - Page title header with blue tint
- `.metric-card-light` - KPI metric cards (requires CSS variables)
- `.financial-card` - Financial summary cards (requires CSS variables)
- `.section-header` - Section title headers

### Alerts
- `.alert-box-orange` - Warning/in-progress alerts
- `.alert-box-purple` - Info/unstarted alerts

### CSS Variables for Cards

When using `.metric-card-light` or `.financial-card`, set these variables:

```html
<div class="metric-card-light" style="
    --card-color: rgba(59, 130, 246, 0.04);
    --card-color-dark: rgba(59, 130, 246, 0.15);
">
    <!-- Card content -->
</div>
```

## Color Palette

### Light Mode
- Background: White gradients with subtle color hints (0.04-0.06 opacity)
- Text: Dark grays (#1e293b, #475569, #64748b)
- Borders: White with high opacity
- Shadows: Subtle blacks (0.04-0.08 opacity)

### Dark Mode
- Background: Dark gradients with stronger color hints (0.15 opacity)
- Text: Light grays (#f1f5f9, #94a3b8, #c4b5fd)
- Borders: White with low opacity
- Shadows: Deeper blacks (0.2-0.4 opacity)

## Extending Styles

To add new style functions:

1. Add function to `theme_styles.py`
2. Export it in `__init__.py`
3. Follow the pattern: light mode media query, then dark mode media query
4. Use consistent naming: `.component-name` for classes

## Benefits

✅ **Centralized**: All styles in one place  
✅ **Maintainable**: Easy to update across all pages  
✅ **Consistent**: Same design language everywhere  
✅ **Accessible**: Adapts to user's system theme  
✅ **Clean Code**: Removes inline CSS clutter from main app

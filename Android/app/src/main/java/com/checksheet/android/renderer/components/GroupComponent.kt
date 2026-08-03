package com.checksheet.android.renderer.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.unit.dp
import com.checksheet.android.data.model.TemplateField
import com.checksheet.android.renderer.DynamicFieldRenderer
import com.checksheet.android.renderer.FieldType
import com.checksheet.android.theme.RailwayTheme
import com.checksheet.android.ui.components.AppCard
import com.checksheet.android.theme.Spacing

/**
 * Reusable Grouped Observation Fields container (Module 29.5, field type 2) - e.g. "Run Test
 * After Assembly" containing "No Load Current"/"Full Load Current"/"Temperature Rise", each of
 * which in turn contains its own leaf fields (U/V/W, RY/YB/BR, ...). None of those labels are
 * hardcoded here: every child field and its label/unit/type comes entirely from [allFields]
 * (matched via [TemplateField.parentFieldId]), so this same component renders any future
 * template's grouping, any depth, any number of sub-fields.
 *
 * This is intentionally NOT registered in [com.checksheet.android.renderer.FieldRendererRegistry]
 * under the standard FieldComponent signature - a group has no scalar value of its own, it needs
 * the full field list and value map to render its children, so [ChecksheetScreen] invokes this
 * directly for top-level GROUP fields on the current page.
 *
 * Module 31: expand/collapse is purely local UI state (which groups are open) - it never touches
 * `values`/`errors`/`onValueChange`, so collapsing a group only hides it visually; its answers
 * (and any validation error) are untouched and still counted when the page is submitted.
 */
@Composable
fun GroupComponent(
    field: TemplateField,
    allFields: List<TemplateField>,
    values: Map<Int, String>,
    errors: Map<Int, String>,
    modifiedFields: Set<Int>,
    onValueChange: (Int, String) -> Unit
) {
    val children = remember(field.id, allFields) {
        allFields.filter { it.parentFieldId == field.id }.sortedBy { it.displayOrder }
    }
    val leafChildren = children.filter { FieldType.fromBackendValue(it.fieldType) != FieldType.GROUP }
    val groupChildren = children.filter { FieldType.fromBackendValue(it.fieldType) == FieldType.GROUP }

    var expanded by rememberSaveable(field.id) { mutableStateOf(true) }
    val chevronRotation by animateFloatAsState(if (expanded) 180f else 0f, tween(150), label = "groupChevron")

    // A group carrying a validation error on any of its own children stays visually distinct even
    // while collapsed, so a Technician isn't left wondering why Submit is blocked.
    val hasError = remember(children, errors, modifiedFields) {
        children.any { it.id in modifiedFields && errors.containsKey(it.id) }
    }

    val cinematic = RailwayTheme.cinematicColors

    AppCard(
        modifier = Modifier
            .fillMaxWidth()
            .border(
                width = 1.dp,
                color = if (hasError) MaterialTheme.colorScheme.error else cinematic.trackSteelDim,
                shape = MaterialTheme.shapes.medium,
            ),
        containerColor = if (hasError) MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.15f) else MaterialTheme.colorScheme.surface,
    ) {
        Column(modifier = Modifier.padding(Spacing.md)) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { expanded = !expanded },
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Row(modifier = Modifier.weight(1f), verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .width(3.dp)
                            .height(20.dp)
                            .clip(MaterialTheme.shapes.extraSmall)
                            .background(if (hasError) MaterialTheme.colorScheme.error else cinematic.wireGlow),
                    )
                    Text(
                        text = field.fieldLabel,
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.padding(start = Spacing.sm),
                    )
                }
                Icon(
                    imageVector = Icons.Filled.ExpandMore,
                    contentDescription = if (expanded) "Collapse" else "Expand",
                    tint = cinematic.wireGlow,
                    modifier = Modifier.rotate(chevronRotation),
                )
            }

            AnimatedVisibility(
                visible = expanded,
                enter = fadeIn(tween(150)) + expandVertically(tween(150)),
                exit = fadeOut(tween(150)) + shrinkVertically(tween(150)),
            ) {
                Column(
                    modifier = Modifier.padding(top = Spacing.sm),
                    verticalArrangement = Arrangement.spacedBy(Spacing.sm)
                ) {
                    // Leaf children (no further nesting) read compactly side by side, e.g. U / V / W -
                    // this layout applies to any group of plain leaf fields, regardless of count or label.
                    if (leafChildren.isNotEmpty()) {
                        leafChildren.chunked(3).forEach { rowFields ->
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(Spacing.sm)
                            ) {
                                rowFields.forEach { child ->
                                    Column(modifier = Modifier.weight(1f)) {
                                        DynamicFieldRenderer(
                                            field = child,
                                            value = values[child.id].orEmpty(),
                                            onValueChange = { newValue -> onValueChange(child.id, newValue) },
                                            errorMessage = if (child.id in modifiedFields) errors[child.id] else null
                                        )
                                    }
                                }
                            }
                        }
                    }

                    // Nested sub-groups (e.g. "No Load Current" inside "Run Test After Assembly") recurse
                    // through this same component - arbitrary nesting depth, per the spec.
                    groupChildren.forEach { child ->
                        GroupComponent(
                            field = child,
                            allFields = allFields,
                            values = values,
                            errors = errors,
                            modifiedFields = modifiedFields,
                            onValueChange = onValueChange
                        )
                    }
                }
            }
        }
    }
}

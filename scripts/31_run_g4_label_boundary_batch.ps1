$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = Join-Path $ProjectRoot ".venv-rdd\Scripts\python.exe"
$Script = Join-Path $ProjectRoot "scripts\26_label_boundary_overlap.py"
$Boxes = Join-Path $ProjectRoot "data_processed\rdd2022_boxes.csv"

$Prefixes = @(
    "g4a_r08_repeat_yolov8n_seed20260513",
    "g4a_r08_repeat_yolov8n_seed20260514",
    "g4b_bridge_yolov8s_seed20260512",
    "g4b_bridge_yolov8s_seed20260513",
    "g4b_bridge_yolov8s_seed20260514"
)

$Splits = @("ordinary", "lodo_all")

foreach ($Prefix in $Prefixes) {
    foreach ($Split in $Splits) {
        $Stem = "${Prefix}_${Split}"
        $Predictions = Join-Path $ProjectRoot "data_processed\predictions\${Stem}_predictions.csv"
        $Csv = Join-Path $ProjectRoot "data_processed\calibration\${Stem}_label_boundary_overlap.csv"
        $AnnotatedCsv = Join-Path $ProjectRoot "data_processed\calibration\${Stem}_label_boundary_overlap_annotated.csv"
        $Summary = Join-Path $ProjectRoot "outputs\g4\${Stem}_label_boundary_overlap_summary.md"

        if (!(Test-Path -LiteralPath $Predictions)) {
            throw "Missing prediction table: $Predictions"
        }

        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Label-boundary overlap: $Stem"
        & $Python $Script `
            --predictions $Predictions `
            --boxes $Boxes `
            --csv $Csv `
            --annotated-csv $AnnotatedCsv `
            --summary $Summary
    }
}

& $Python (Join-Path $ProjectRoot "scripts\30_summarize_g4_label_boundary.py")

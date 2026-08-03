import { Skeleton, TableBody, TableCell, TableRow } from '@mui/material';

interface TableSkeletonProps {
  rows?: number;
  columns: number;
}

/**
 * Module 33: shared "animated table placeholder" - a shimmering skeleton row set matching the
 * real table's column count, shown while data loads instead of (or in addition to) a spinner.
 * Reuses MUI's own Skeleton (themed with the cyber palette in theme.ts) rather than a bespoke
 * shimmer implementation.
 */
export default function TableSkeleton({ rows = 6, columns }: TableSkeletonProps) {
  return (
    <TableBody>
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <TableRow key={rowIndex}>
          {Array.from({ length: columns }).map((__, colIndex) => (
            <TableCell key={colIndex}>
              <Skeleton variant="text" height={22} width={colIndex === 0 ? '60%' : '80%'} />
            </TableCell>
          ))}
        </TableRow>
      ))}
    </TableBody>
  );
}

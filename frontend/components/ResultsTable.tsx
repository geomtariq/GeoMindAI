'use client';

interface ResultsTableProps {
  results: any[];
}

export default function ResultsTable({ results }: ResultsTableProps) {
  if (!results || results.length === 0) {
    return null;
  }

  const headers = Object.keys(results[0]);

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
      <thead>
        <tr>
          {headers.map((header) => (
            <th key={header} style={{ border: '1px solid black', padding: '8px', backgroundColor: '#f2f2f2' }}>
              {header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {results.map((row, index) => (
          <tr key={index}>
            {headers.map((header) => (
              <td key={header} style={{ border: '1px solid black', padding: '8px' }}>
                {row[header]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

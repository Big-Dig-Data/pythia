<template>
  <v-simple-table fixed-header dense :height="height - 8" class="px-2 pb-2">
    <thead>
      <tr>
        <th v-for="col in columns" :key="col.name">{{ col.name }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(row, index) in rows" :key="index">
        <td v-for="(col, index) in columns" :key="col.name">
          {{ row[index] }}
        </td>
      </tr>
    </tbody>
  </v-simple-table>
</template>

<script>
export default {
  name: "ChartTable",
  props: {
    columns: { required: true, type: Array },
    rawData: { required: true, type: Array },
    height: { required: true, type: Number },
  },

  computed: {
    rows() {
      return this.rawData.map((obj) => {
        return this.columns.map((col) => obj[col.value]);
      });
    },
  },
};
</script>

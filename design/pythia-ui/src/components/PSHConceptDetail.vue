<i18n src="../locales/common.yaml"></i18n>
<i18n>
en:
  score: Score
  work_count: Work count
  avg_score: Average score
  work_count_total: All associated works
  work_count_direct: Directly associated works (not from descendants)
  publisher: Publisher
  ratio: Ratio
  author: Author
  work: Work
  score_rel: Relative interest
  total_score_rel: Relative interest in whole catalogue
  language: Language
  title:
    authors: Most popular authors
    publishers: Most popular publishers
    works: Most demanded works
    langs: Most popular languages

cs:
  score: Skóre
  work_count: Počet prací
  avg_score: Průměrné skóre
  work_count_total: Všechna asociovaná díla
  work_count_direct: Přímo asociovaná díla (bez potomků)
  publisher: Vydavatel
  ratio: Poměr
  author: Autor
  work: Dílo
  score_rel: Relativní zájem
  total_score_rel: Relativní zájem v celém katalogu
  language: Jazyk
  title:
    authors: Nejpopulárnější autoři
    publishers: Nejpopulárnější vydavatelé
    works: Nejpoptávanější díla
    langs: Nejpopulárnější jazyky
</i18n>

<template>
  <div v-if="concept" class="concept-card sticky elevation-2 ml-2">
    <div class="ancestry">
      <span v-for="(ancestor, index) in concept.ancestors" :key="index">
        {{ ancestor.name_cs }}
        <v-icon small class="align-bl">fa-angle-double-right</v-icon>
      </span>
    </div>
    <h3 class="display-1 text-xs-center name">{{ concept.name_cs }}</h3>
    <h4 class="pshid text-xs-center">{{ concept.pshid }}</h4>
    <table class="listing">
      <tr>
        <th>{{ $t("work_count") }}</th>
        <td>
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <span v-on="on">
                {{ concept.direct_work_count }} / {{ concept.work_count }}
              </span>
            </template>
            <span>
              {{ $t("work_count_total") }}: {{ concept.work_count }}<br />
              {{ $t("work_count_direct") }}: {{ concept.direct_work_count }}
            </span>
          </v-tooltip>
        </td>
      </tr>
      <tr>
        <th>{{ $t("score") }}</th>
        <td class="text-xs-right">{{ formatNumber(concept.score) }}</td>
      </tr>
    </table>
    <!-- publishers -->
    <h3 class="headline pt-2">{{ $t("title.publishers") }}</h3>
    <v-data-table
      :headers="[
        { text: $t('publisher'), value: 'publisher' },
        { text: $t('score'), value: 'score', align: 'right' },
        { text: $t('work_count'), value: 'work_count', align: 'right' },
        { text: $t('ratio'), value: 'ratio', align: 'right' },
      ]"
      :items="concept.publishers"
      :footer-props="{ 'items-per-page-text': $t('table.rows_per_page') }"
      :sort-by="null"
    >
      <template v-slot:item.score="{ item }">
        {{ formatNumber(item.score) }}
      </template>
      <template v-slot:item.ratio="{ item }">
        {{ formatNumber(item.ratio) }}
      </template>
    </v-data-table>
    <!-- authors -->
    <h3 class="headline pt-2">{{ $t("title.authors") }}</h3>
    <v-data-table
      :headers="[
        { text: $t('author'), value: 'author.name' },
        { text: $t('score'), value: 'score', align: 'right' },
        { text: $t('work_count'), value: 'work_count', align: 'right' },
      ]"
      :items="concept.authors"
      :footer-props="{ 'items-per-page-text': $t('table.rows_per_page') }"
      :sort-by="null"
    >
      <template v-slot:item.score="{ item }">
        {{ formatNumber(item.score) }}
      </template>
      <template v-slot:item.author.name="{ item }">
        <router-link
          :to="{ name: 'author detail', params: { authorId: item.author.pk } }"
          >{{ item.author.name }}</router-link
        >
      </template>
    </v-data-table>

    <!-- works -->
    <h3 class="headline pt-2">{{ $t("title.works") }}</h3>
    <v-data-table
      :headers="[
        { text: $t('work'), value: 'work.name' },
        { text: $t('score'), value: 'hit_score', align: 'right' },
      ]"
      :items="concept.works"
      :footer-props="{ 'items-per-page-text': $t('table.rows_per_page') }"
      :sort-by="null"
    >
      <template v-slot:item.hit_score="{ item }">
        {{ formatNumber(item.hit_score) }}
      </template>
      <template v-slot:item.work.name="{ item }">
        <router-link
          :to="{ name: 'work detail', params: { workId: item.work.pk } }"
          >{{ item.work.name }}</router-link
        >
      </template>
    </v-data-table>

    <!-- languages -->
    <h3 class="headline pt-2">{{ $t("title.langs") }}</h3>
    <v-data-table
      :headers="[
        { text: $t('language'), value: 'language' },
        { text: $t('work_count'), value: 'work_count', align: 'right' },
        { text: $t('score'), value: 'score', align: 'right' },
        {
          text: $t('score_rel'),
          value: 'score_rel',
          align: 'right',
          sortable: false,
        },
        {
          text: $t('total_score_rel'),
          value: 'total_rel_score',
          align: 'right',
        },
      ]"
      :items="concept.languages"
      :footer-props="{ 'items-per-page-text': $t('table.rows_per_page') }"
      :sort-by="null"
    >
      <template v-slot:item.score="{ item }">
        {{ formatNumber(item.score) }}
      </template>
      <template v-slot:item.score_rel="{ item }">
        <span
          :class="
            item.score / concept.score > item.total_rel_score
              ? 'text-green'
              : 'text-red'
          "
          >{{ formatNumber((100 * item.score) / concept.score) }} %</span
        >
      </template>
      <template v-slot:item.total_rel_score="{ item }">
        {{ formatNumber(100 * item.total_rel_score) }} %
      </template>
    </v-data-table>
  </div>
  <div v-else-if="loading" class="full-width sticky">
    <v-progress-circular
      :size="70"
      :width="7"
      color="primary"
      indeterminate
    ></v-progress-circular>
  </div>
</template>
<script>
import * as math from "mathjs";
import axios from "axios";
export default {
  name: "PSHConceptDetail",
  props: {
    miUUID: { required: true },
    pshid: { required: true },
  },
  data() {
    return {
      concept: null,
      numberFormat: {
        notation: "fixed",
        precision: 1,
      },
      loading: false,
    };
  },
  methods: {
    formatNumber(number) {
      return math.format(number, this.numberFormat);
    },
    fetchData() {
      this.loading = true;
      axios.get(`/api/bookrank/mi/${this.miUUID}/psh-topic/${this.pshid}`).then(
        (response) => {
          this.concept = response.data;
          this.loading = false;
        },
        (error) => {
          this.$store.dispatch("showSnackbar", {
            content: "Error fetching data: " + error,
          });
          this.loading = false;
        }
      );
    },
  },
  created() {
    this.fetchData();
  },
  watch: {
    // pshid () {
    //   this.fetchData()
    // }
  },
};
</script>

<style scoped lang="scss">
div.full-width {
  width: 100%;
  text-align: center;
}
div.sticky {
  position: sticky;
  top: 6rem;
}

div.concept-card {
  padding: 1.5rem;
  max-height: 90vh;
  overflow: scroll;

  .name {
    padding: 1.5rem 1rem 0.25rem 1rem;
  }

  .ancestry {
    color: #888888;
    i.v-icon.align-bl {
      vertical-align: baseline;
      color: inherit;
    }
  }
  .pshid {
    color: #888888;
    padding-bottom: 2rem;
  }
}

span.text-red {
  color: red;
}
span.text-green {
  color: green;
}
</style>
